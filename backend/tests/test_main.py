from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_checks():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_resource_not_found():
    response = client.get("/api/v1/nonexistent-endpoint-abc-123")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert "message" in data["error"]

def test_validation_error():
    # Sending invalid data (e.g. missing required fields) to register endpoint
    response = client.post("/api/v1/auth/register", json={"email": "invalid_email_no_other_fields"})
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert len(data["error"]["details"]) > 0
    # Details should specify missing fields
    details = data["error"]["details"]
    fields = [d["field"] for d in details]
    assert "password" in fields or "body.password" in fields or any("password" in f for f in fields)
