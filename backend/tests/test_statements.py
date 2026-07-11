import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.models.statement import Statement, StatementStatus
from app.utils.security import get_password_hash

client = TestClient(app)

def test_statement_upload_validation_and_pagination(db_session, monkeypatch):
    # Mock celery task call delay() to do nothing
    from app.workers.tasks import process_statement_task
    monkeypatch.setattr(process_statement_task, "delay", lambda *args, **kwargs: None)

    # 1. Setup user & authenticate
    hashed = get_password_hash("testpassword123")
    user = User(
        email="statementtest@example.com",
        password_hash=hashed,
        name="Statement Test",
        currency="INR",
        failed_login_attempts=0,
    )
    db_session.add(user)
    db_session.commit()

    # Login to get auth token
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "statementtest@example.com", "password": "testpassword123"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test Invalid MIME type
    bad_file = ("test.txt", io.BytesIO(b"Hello world"), "text/plain")
    resp = client.post(
        "/api/v1/statements/upload",
        files={"file": bad_file},
        headers=headers
    )
    assert resp.status_code == 400
    assert "Only PDF and CSV files are supported" in resp.json()["error"]["message"]

    # 3. Test File Size Limit Exceeded (10MB limit)
    large_file = ("large.pdf", io.BytesIO(b"0" * (11 * 1024 * 1024)), "application/pdf") # 11MB
    resp = client.post(
        "/api/v1/statements/upload",
        files={"file": large_file},
        headers=headers
    )
    assert resp.status_code == 413
    assert "exceeds maximum limit of 10MB" in resp.json()["error"]["message"]

    # 4. Test Valid PDF Upload
    valid_file = ("statement.pdf", io.BytesIO(b"%PDF-1.4 dummy pdf content"), "application/pdf")
    resp = client.post(
        "/api/v1/statements/upload",
        files={"file": valid_file},
        headers=headers
    )

    assert resp.status_code == 201
    statement_data = resp.json()
    assert statement_data["file_name"] == "statement.pdf"
    assert statement_data["status"] == "pending"

    # Create additional statements to test pagination
    for i in range(5):
        stmt = Statement(
            user_id=user.id,
            file_name=f"stmt_{i}.pdf",
            file_url=f"mock://stmt_{i}.pdf",
            status=StatementStatus.pending
        )
        db_session.add(stmt)
    db_session.commit()

    # 5. Test paginated get statements list
    # Fetch first page with limit 3
    list_resp = client.get("/api/v1/statements/?page=1&limit=3", headers=headers)
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert "items" in list_data
    assert list_data["total"] == 6 # 1 uploaded + 5 manually added
    assert len(list_data["items"]) == 3
    assert list_data["page"] == 1
    assert list_data["limit"] == 3

    # Fetch second page
    list_resp = client.get("/api/v1/statements/?page=2&limit=3", headers=headers)
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert len(list_data["items"]) == 3
    assert list_data["page"] == 2
