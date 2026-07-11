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

