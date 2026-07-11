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

def test_config_validation():
    import pytest
    from pydantic import ValidationError
    from app.config import Settings

    # Valid config in development
    dev_settings = Settings(ENVIRONMENT="development", DATABASE_URL="sqlite:///./test.db", SECRET_KEY="your-jwt-secret-256-bit")
    assert dev_settings.ENVIRONMENT == "development"

    # Invalid config in production: default secret key
    with pytest.raises(ValidationError) as excinfo:
        Settings(ENVIRONMENT="production", DATABASE_URL="postgresql://localhost/db", SECRET_KEY="your-jwt-secret-256-bit")
    assert "SECRET_KEY must be changed from default" in str(excinfo.value)

    # Invalid config in production: short secret key
    with pytest.raises(ValidationError) as excinfo:
        Settings(ENVIRONMENT="production", DATABASE_URL="postgresql://localhost/db", SECRET_KEY="short-key")
    assert "SECRET_KEY must be at least 32 characters" in str(excinfo.value)

    # Invalid config in production: sqlite database URL
    with pytest.raises(ValidationError) as excinfo:
        Settings(ENVIRONMENT="production", DATABASE_URL="sqlite:///./test.db", SECRET_KEY="a" * 32)
    assert "DATABASE_URL must be a PostgreSQL connection string" in str(excinfo.value)

    # Valid config in production
    prod_settings = Settings(ENVIRONMENT="production", DATABASE_URL="postgresql://localhost/db", SECRET_KEY="a" * 32)
    assert prod_settings.ENVIRONMENT == "production"

