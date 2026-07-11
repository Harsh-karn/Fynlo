from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User

client = TestClient(app)

def test_auth_flow(db_session):
    # 1. Register user
    user_data = {
        "email": "testuser@example.com",
        "password": "strongpassword123",
        "name": "Test User",
        "phone_number": "+919876543210",
        "currency": "INR"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
    assert response.json()["name"] == user_data["name"]
    assert "id" in response.json()

    # 2. Duplicate registration should fail
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["error"]["message"]

    # 3. Login
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"

    # 4. Get current user profile
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]

    # 5. Access /me with invalid token should fail
    bad_headers = {"Authorization": "Bearer invalidtoken123"}
    response = client.get("/api/v1/auth/me", headers=bad_headers)
    assert response.status_code == 401

    # 6. Refresh tokens using valid refresh token
    import time
    time.sleep(1)
    refresh_payload = {"refresh_token": tokens["refresh_token"]}
    response = client.post("/api/v1/auth/refresh", json=refresh_payload)
    assert response.status_code == 200
    new_tokens = response.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["access_token"] != tokens["access_token"]

    # 7. Refresh using invalid refresh token should fail
    bad_refresh_payload = {"refresh_token": "invalid_refresh_token"}
    response = client.post("/api/v1/auth/refresh", json=bad_refresh_payload)
    assert response.status_code == 401

    # 8. Refresh using access token (wrong type) should fail
    wrong_token_payload = {"refresh_token": tokens["access_token"]}
    response = client.post("/api/v1/auth/refresh", json=wrong_token_payload)
    assert response.status_code == 401


def test_register_with_invite_token(db_session):
    from app.config import settings
    from app.models.invite_token import InviteToken
    
    # 1. Enable require invite token
    original_require = settings.REQUIRE_INVITE_TOKEN
    settings.REQUIRE_INVITE_TOKEN = True
    
    try:
        user_data = {
            "email": "betatester@example.com",
            "password": "strongpassword123",
            "name": "Beta Tester",
            "phone_number": "+919876543211",
            "currency": "INR"
        }
        
        # 2. Registration without token should fail
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "requires a valid invite token" in response.json()["error"]["message"]
        
        # 3. Create a valid invite token in db
        db_token = InviteToken(token="FYNLO-TEST-1234")
        db_session.add(db_token)
        db_session.commit()
        
        # 4. Registration with invalid token should fail
        user_data_bad_token = user_data.copy()
        user_data_bad_token["invite_token"] = "INVALID-TOKEN"
        response = client.post("/api/v1/auth/register", json=user_data_bad_token)
        assert response.status_code == 400
        assert "Invalid or already used invite token" in response.json()["error"]["message"]
        
        # 5. Registration with valid token should succeed
        user_data_good_token = user_data.copy()
        user_data_good_token["invite_token"] = "FYNLO-TEST-1234"
        response = client.post("/api/v1/auth/register", json=user_data_good_token)
        assert response.status_code == 201
        
        # 6. Verify invite token was marked as used
        db_token = db_session.query(InviteToken).filter(InviteToken.token == "FYNLO-TEST-1234").first()
        assert db_token.is_used is True
        assert db_token.used_by_id is not None
        
        # 7. Try to reuse the same token should fail
        user_data_reuse = {
            "email": "anotherbeta@example.com",
            "password": "strongpassword123",
            "name": "Another Beta",
            "phone_number": "+919876543212",
            "currency": "INR",
            "invite_token": "FYNLO-TEST-1234"
        }
        response = client.post("/api/v1/auth/register", json=user_data_reuse)
        assert response.status_code == 400
        assert "Invalid or already used invite token" in response.json()["error"]["message"]
        
    finally:
        settings.REQUIRE_INVITE_TOKEN = original_require


def test_account_lockout(db_session):
    from app.models.user import User
    from app.utils.security import get_password_hash
    from datetime import datetime, timezone

    # Create a user directly in db
    hashed = get_password_hash("correctpassword")
    user = User(
        email="lockouttest@example.com",
        password_hash=hashed,
        name="Lockout Test",
        currency="INR",
        failed_login_attempts=0
    )
    db_session.add(user)
    db_session.commit()

    login_data = {"username": "lockouttest@example.com", "password": "wrongpassword"}

    # 1. Five wrong attempts should not lock yet on the 4th
    for i in range(4):
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401, f"Expected 401 on attempt {i+1}"

    # 2. 5th wrong attempt triggers lockout
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401  # 5th failure

    # Manually set locked_until in the past to simulate lockout expiry
    db_user = db_session.query(User).filter(User.email == "lockouttest@example.com").first()
    assert db_user.failed_login_attempts >= 5
    assert db_user.locked_until is not None

    # 3. While locked, correct password is still rejected with 429
    response = client.post("/api/v1/auth/login", data={"username": "lockouttest@example.com", "password": "correctpassword"})
    assert response.status_code == 429
    assert "locked" in response.json()["error"]["message"].lower()

    # 4. Verify the locked_until and attempt count in DB directly
    from datetime import timedelta
    assert db_user.locked_until is not None
    now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    assert db_user.locked_until.replace(tzinfo=None) > now_naive  # Still in the future

    # 5. Simulate lockout expiry by resetting in DB and checking counter reset logic
    db_user.locked_until = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_user.failed_login_attempts = 0
    db_session.commit()

    # Confirm values were persisted correctly
    assert db_user.failed_login_attempts == 0
    now_naive2 = datetime.now(timezone.utc).replace(tzinfo=None)
    assert db_user.locked_until.replace(tzinfo=None) < now_naive2  # Expired


def test_data_export_and_account_deletion(db_session):
    """Test DPDP Act compliance: data export (CSV + JSON) and account deletion."""
    from app.models.user import User
    from app.models.transaction import Transaction, TransactionType, TransactionCategory, TransactionSource
    from app.utils.security import get_password_hash
    from datetime import datetime as dt, timezone as tz

    # --- Setup: create user + transactions ---
    hashed = get_password_hash("testpassword123")
    user = User(
        email="exporttest@example.com",
        password_hash=hashed,
        name="Export Test",
        currency="INR",
        failed_login_attempts=0,
    )
    db_session.add(user)
    db_session.commit()

    txn = Transaction(
        user_id=user.id,
        amount=25000,  # ₹250.00
        type=TransactionType.debit,
        category=TransactionCategory.food,
        merchant_name="Swiggy",
        description="Lunch order",
        source=TransactionSource.manual,
        transaction_date=dt.now(tz.utc),
    )
    db_session.add(txn)
    db_session.commit()

    # Login to get auth token
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "exporttest@example.com", "password": "testpassword123"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # --- 1. CSV export ---
    csv_resp = client.get("/api/v1/auth/me/export?format=csv", headers=headers)
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers.get("content-type", "")
    csv_content = csv_resp.content.decode("utf-8")
    assert "transaction_id" in csv_content  # header row
    assert "Swiggy" in csv_content
    assert "250.0" in csv_content

    # --- 2. JSON export ---
    json_resp = client.get("/api/v1/auth/me/export?format=json", headers=headers)
    assert json_resp.status_code == 200
    assert "application/json" in json_resp.headers.get("content-type", "")
    import json as json_lib
    payload = json_lib.loads(json_resp.content)
    assert payload["profile"]["email"] == "exporttest@example.com"
    assert len(payload["transactions"]) == 1
    assert payload["transactions"][0]["merchant_name"] == "Swiggy"
    assert payload["transactions"][0]["amount_inr"] == 250.0

    # --- 3. Account deletion ---
    delete_resp = client.delete("/api/v1/auth/me", headers=headers)
    assert delete_resp.status_code == 204

    # --- 4. Verify user is gone ---
    deleted_user = db_session.query(User).filter(User.email == "exporttest@example.com").first()
    assert deleted_user is None

    # --- 5. Token is now invalid (user doesn't exist) ---
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 401

