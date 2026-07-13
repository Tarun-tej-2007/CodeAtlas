import pytest
import jwt
import uuid
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from app.core.jwt import TokenType
from app.models.user import User

# Helper to create expired tokens for tests
def create_expired_token(subject: str, token_type: TokenType) -> str:
    now = datetime.now(timezone.utc)
    exp = now - timedelta(minutes=10)
    payload = {
        "sub": subject,
        "iat": now - timedelta(minutes=20),
        "exp": exp,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "token_type": token_type.value,
    }
    if token_type == TokenType.REFRESH:
        payload["jti"] = str(uuid.uuid4())
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

# --- 1. Registration Tests ---

def test_registration_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "taruntej",
            "email": "taruntej@example.com",
            "password": "StrongPassword123!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"
    assert "user" in data
    assert data["user"]["username"] == "taruntej"
    assert data["user"]["email"] == "taruntej@example.com"
    assert "id" in data["user"]
    # Verify sensitive hash fields are not exposed in standard responses
    assert "password_hash" not in data["user"]
    assert "hashed_password" not in data["user"]

def test_registration_duplicate_email(client):
    payload = {
        "username": "tarun1",
        "email": "duplicate@example.com",
        "password": "StrongPassword123!"
    }
    # First registration
    client.post("/api/v1/auth/register", json=payload)
    
    # Second registration with same email, different username
    payload["username"] = "tarun2"
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert "email" in response.json()["detail"].lower()

def test_registration_duplicate_username(client):
    payload = {
        "username": "duplicate_user",
        "email": "tarun1@example.com",
        "password": "StrongPassword123!"
    }
    # First registration
    client.post("/api/v1/auth/register", json=payload)
    
    # Second registration with same username, different email
    payload["email"] = "tarun2@example.com"
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert "username" in response.json()["detail"].lower()

@pytest.mark.parametrize(
    "payload",
    [
        {"username": "", "email": "tarun@example.com", "password": "Password123!"},  # Empty username
        {"username": "tarun", "email": "invalid-email", "password": "Password123!"},  # Invalid email format
        {"username": "tarun", "email": "tarun@example.com", "password": ""},          # Empty password
        {"username": "ta", "email": "tarun@example.com", "password": "Password123!"}, # Username too short
    ]
)
def test_registration_invalid_payloads(client, payload):
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422

# --- 2. Login Tests ---

def test_login_success_via_email(client):
    # Register user
    client.post(
        "/api/v1/auth/register",
        json={"username": "tarun", "email": "tarun@example.com", "password": "Password123!"}
    )
    # Login via email
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "tarun@example.com", "password": "Password123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"

def test_login_success_via_username(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "tarun", "email": "tarun@example.com", "password": "Password123!"}
    )
    # Login via username
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "tarun", "password": "Password123!"}
    )
    assert response.status_code == 200

def test_login_invalid_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "tarun", "email": "tarun@example.com", "password": "Password123!"}
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "tarun", "password": "WrongPassword123!"}
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()

def test_login_unknown_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "nonexistent", "password": "Password123!"}
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()

def test_login_inactive_user(client, db_session):
    # Register user
    reg_response = client.post(
        "/api/v1/auth/register",
        json={"username": "inactive", "email": "inactive@example.com", "password": "Password123!"}
    )
    user_id = reg_response.json()["user"]["id"]
    
    # Set inactive in database
    user = db_session.query(User).filter(User.id == uuid.UUID(user_id)).first()
    user.is_active = False
    db_session.commit()
    
    # Attempt login
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "inactive", "password": "Password123!"}
    )
    assert response.status_code == 403
    assert "deactivated" in response.json()["detail"].lower()

# --- 3. Current User Tests ---

def test_current_user_success(client):
    reg_response = client.post(
        "/api/v1/auth/register",
        json={"username": "tarun", "email": "tarun@example.com", "password": "Password123!"}
    )
    access_token = reg_response.json()["access_token"]
    
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "tarun"
    assert data["email"] == "tarun@example.com"
    assert "id" in data
    assert "password_hash" not in data

def test_current_user_missing_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_current_user_invalid_token(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer fake_token_value"}
    )
    assert response.status_code == 401

def test_current_user_expired_token(client):
    expired_token = create_expired_token(str(uuid.uuid4()), TokenType.ACCESS)
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401

# --- 4. Refresh Token Tests ---

def test_refresh_token_success(client):
    reg_response = client.post(
        "/api/v1/auth/register",
        json={"username": "tarun", "email": "tarun@example.com", "password": "Password123!"}
    )
    refresh_token = reg_response.json()["refresh_token"]
    
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert "expires_in" in data

def test_refresh_token_invalid_token(client):
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "fake_refresh_token"}
    )
    assert response.status_code == 401

def test_refresh_token_expired_token(client):
    expired_refresh = create_expired_token(str(uuid.uuid4()), TokenType.REFRESH)
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": expired_refresh}
    )
    assert response.status_code == 401

def test_refresh_token_access_token_supplied(client):
    reg_response = client.post(
        "/api/v1/auth/register",
        json={"username": "tarun", "email": "tarun@example.com", "password": "Password123!"}
    )
    access_token = reg_response.json()["access_token"]
    
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token}
    )
    assert response.status_code == 401

# --- 5. Logout Tests ---

def test_logout_success(client):
    reg_response = client.post(
        "/api/v1/auth/register",
        json={"username": "tarun", "email": "tarun@example.com", "password": "Password123!"}
    )
    refresh_token = reg_response.json()["refresh_token"]
    
    response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 204
    
    # Assert refresh token can no longer be used to fetch fresh access token
    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 401

def test_logout_twice_idempotent(client):
    reg_response = client.post(
        "/api/v1/auth/register",
        json={"username": "tarun", "email": "tarun@example.com", "password": "Password123!"}
    )
    refresh_token = reg_response.json()["refresh_token"]
    
    # Logout 1
    response1 = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token}
    )
    assert response1.status_code == 204
    
    # Logout 2
    response2 = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token}
    )
    assert response2.status_code == 204

def test_logout_invalid_token(client):
    response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": "fake_token"}
    )
    assert response.status_code == 401

def test_logout_access_token_supplied(client):
    reg_response = client.post(
        "/api/v1/auth/register",
        json={"username": "tarun", "email": "tarun@example.com", "password": "Password123!"}
    )
    access_token = reg_response.json()["access_token"]
    
    response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": access_token}
    )
    assert response.status_code == 401
