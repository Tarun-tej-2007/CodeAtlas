import pytest
import uuid
from app.models.enums import ProjectVisibility

def test_create_project_success(client):
    # Register user to acquire token
    reg_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "projectcreator",
            "email": "creator@example.com",
            "password": "Password123!"
        }
    )
    assert reg_response.status_code == 201
    access_token = reg_response.json()["access_token"]
    user_id = reg_response.json()["user"]["id"]

    # Create project
    response = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "CodeAtlas Backend Engine",
            "description": "Core visualization platform service.",
            "visibility": "PRIVATE"

        }
    )

    assert response.status_code == 201
    assert "Location" in response.headers
    data = response.json()
    assert response.headers["Location"] == f"/api/v1/projects/{data['id']}"
    assert data["owner_id"] == user_id
    assert data["name"] == "CodeAtlas Backend Engine"
    assert data["slug"] == "codeatlas-backend-engine"
    assert data["description"] == "Core visualization platform service."
    assert data["visibility"] == "PRIVATE"
    assert "created_at" in data
    assert "updated_at" in data

def test_create_project_slug_auto_counter(client):
    reg_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "slugcreator",
            "email": "slug@example.com",
            "password": "Password123!"
        }
    )
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # First project
    res1 = client.post("/api/v1/projects", headers=headers, json={"name": "My Workspace"})
    assert res1.status_code == 201
    assert res1.json()["slug"] == "my-workspace"

    # Second project with identical name
    res2 = client.post("/api/v1/projects", headers=headers, json={"name": "My Workspace"})
    assert res2.status_code == 201
    assert res2.json()["slug"] == "my-workspace-2"

def test_create_project_unauthenticated(client):
    response = client.post(
        "/api/v1/projects",
        json={"name": "Unauthenticated Project"}
    )
    assert response.status_code == 401

@pytest.mark.parametrize(
    "payload",
    [
        {"name": ""},                   # Empty name
        {"name": "     "},              # Whitespace only
        {"name": "a" * 151},            # Name too long
        {"name": "Valid", "description": "d" * 501}, # Description too long
    ]
)
def test_create_project_invalid_payload(client, payload):
    reg_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "valuser",
            "email": "val@example.com",
            "password": "Password123!"
        }
    )
    token = reg_response.json()["access_token"]

    response = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    assert response.status_code == 422
