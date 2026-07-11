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
