import pytest
import uuid
from app.models.enums import ProjectVisibility

# --- POST /api/v1/projects Tests ---

def test_create_project_success(client):
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

    res1 = client.post("/api/v1/projects", headers=headers, json={"name": "My Workspace"})
    assert res1.status_code == 201
    assert res1.json()["slug"] == "my-workspace"

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


# --- GET /api/v1/projects Tests ---

def test_list_projects_unauthenticated(client):
    response = client.get("/api/v1/projects")
    assert response.status_code == 401

def test_list_projects_empty(client):
    reg_response = client.post(
        "/api/v1/auth/register",
        json={"username": "emptyuser", "email": "empty@example.com", "password": "Password123!"}
    )
    token = reg_response.json()["access_token"]

    response = client.get(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["count"] == 0
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["size"] == 20
    assert data["pages"] == 0
    assert data["has_next"] is False
    assert data["has_previous"] is False

def test_list_projects_visibility_and_isolation(client):
    # Register User A & User B
    u_a = client.post(
        "/api/v1/auth/register",
        json={"username": "usera", "email": "usera@example.com", "password": "Password123!"}
    ).json()
    u_b = client.post(
        "/api/v1/auth/register",
        json={"username": "userb", "email": "userb@example.com", "password": "Password123!"}
    ).json()

    token_a = u_a["access_token"]
    token_b = u_b["access_token"]

    # User A creates 1 private project & 1 public project
    client.post("/api/v1/projects", headers={"Authorization": f"Bearer {token_a}"}, json={"name": "A Private", "visibility": "PRIVATE"})
    client.post("/api/v1/projects", headers={"Authorization": f"Bearer {token_a}"}, json={"name": "A Public", "visibility": "PUBLIC"})

    # User B creates 1 private project
    client.post("/api/v1/projects", headers={"Authorization": f"Bearer {token_b}"}, json={"name": "B Private", "visibility": "PRIVATE"})

    # User B lists projects: should see B Private + A Public (total = 2), but NOT A Private!
    res_b = client.get("/api/v1/projects", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.status_code == 200
    data_b = res_b.json()
    names_b = [item["name"] for item in data_b["items"]]
    assert "B Private" in names_b
    assert "A Public" in names_b
    assert "A Private" not in names_b
    assert data_b["total"] == 2

def test_list_projects_pagination(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "pageuser", "email": "page@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    # Create 5 projects
    for i in range(1, 6):
        client.post("/api/v1/projects", headers=headers, json={"name": f"Project {i}"})

    # Fetch Page 1 (size=2)
    res_p1 = client.get("/api/v1/projects?page=1&size=2", headers=headers)
    assert res_p1.status_code == 200
    d1 = res_p1.json()
    assert d1["count"] == 2
    assert d1["total"] == 5
    assert d1["page"] == 1
    assert d1["size"] == 2
    assert d1["pages"] == 3
    assert d1["has_next"] is True
    assert d1["has_previous"] is False

    # Fetch Page 2 (size=2)
    res_p2 = client.get("/api/v1/projects?page=2&size=2", headers=headers)
    assert res_p2.status_code == 200
    d2 = res_p2.json()
    assert d2["count"] == 2
    assert d2["page"] == 2
    assert d2["has_next"] is True
    assert d2["has_previous"] is True

    # Fetch Page 3 (size=2)
    res_p3 = client.get("/api/v1/projects?page=3&size=2", headers=headers)
    assert res_p3.status_code == 200
    d3 = res_p3.json()
    assert d3["count"] == 1
    assert d3["page"] == 3
    assert d3["has_next"] is False
    assert d3["has_previous"] is True

def test_list_projects_sorting(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "sortuser", "email": "sort@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    client.post("/api/v1/projects", headers=headers, json={"name": "Beta Workspace"})
    client.post("/api/v1/projects", headers=headers, json={"name": "Alpha Workspace"})
    client.post("/api/v1/projects", headers=headers, json={"name": "Gamma Workspace"})

    # Sort by name asc
    res_asc = client.get("/api/v1/projects?sort_by=name&order=asc", headers=headers)
    assert res_asc.status_code == 200
    names_asc = [p["name"] for p in res_asc.json()["items"]]
    assert names_asc == ["Alpha Workspace", "Beta Workspace", "Gamma Workspace"]

    # Sort by name desc
    res_desc = client.get("/api/v1/projects?sort_by=name&order=desc", headers=headers)
    assert res_desc.status_code == 200
    names_desc = [p["name"] for p in res_desc.json()["items"]]
    assert names_desc == ["Gamma Workspace", "Beta Workspace", "Alpha Workspace"]

def test_list_projects_search(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "searchuser", "email": "search@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    client.post("/api/v1/projects", headers=headers, json={"name": "AST Engine", "description": "Python AST Parser"})
    client.post("/api/v1/projects", headers=headers, json={"name": "Visualizer Map", "description": "Renders node graph"})

    # Search in name
    res_ast = client.get("/api/v1/projects?search=ast", headers=headers)
    assert res_ast.status_code == 200
    items_ast = res_ast.json()["items"]
    assert len(items_ast) == 1
    assert items_ast[0]["name"] == "AST Engine"

    # Search in description
    res_graph = client.get("/api/v1/projects?search=node", headers=headers)
    assert res_graph.status_code == 200
    items_graph = res_graph.json()["items"]
    assert len(items_graph) == 1
    assert items_graph[0]["name"] == "Visualizer Map"

def test_list_projects_visibility_filter(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "visuser", "email": "vis@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    client.post("/api/v1/projects", headers=headers, json={"name": "Priv 1", "visibility": "PRIVATE"})
    client.post("/api/v1/projects", headers=headers, json={"name": "Pub 1", "visibility": "PUBLIC"})

    # Filter PRIVATE
    res_priv = client.get("/api/v1/projects?visibility=PRIVATE", headers=headers)
    assert res_priv.status_code == 200
    items_priv = res_priv.json()["items"]
    assert len(items_priv) == 1
    assert items_priv[0]["name"] == "Priv 1"

    # Filter PUBLIC
    res_pub = client.get("/api/v1/projects?visibility=PUBLIC", headers=headers)
    assert res_pub.status_code == 200
    items_pub = res_pub.json()["items"]
    assert len(items_pub) == 1
    assert items_pub[0]["name"] == "Pub 1"

@pytest.mark.parametrize(
    "query_str",
    [
        "page=0",                 # Page < 1
        "size=0",                 # Size < 1
        "size=101",               # Size > 100
        "sort_by=invalid_field",  # Invalid sort_by
        "order=invalid_order",    # Invalid order
        "visibility=INVALID_VIS", # Invalid visibility
    ]
)
def test_list_projects_invalid_query_parameters(client, query_str):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "invuser", "email": "inv@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    response = client.get(f"/api/v1/projects?{query_str}", headers=headers)
    assert response.status_code == 422
