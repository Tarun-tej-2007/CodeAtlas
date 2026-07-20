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


# --- GET /api/v1/projects/{project_id} Tests ---

def test_get_project_detail_owner_success(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "detailowner", "email": "detailowner@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    create_res = client.post("/api/v1/projects", headers=headers, json={"name": "Private Project Detail", "visibility": "PRIVATE"})
    project_id = create_res.json()["id"]

    response = client.get(f"/api/v1/projects/{project_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Private Project Detail"
    assert data["visibility"] == "PRIVATE"

def test_get_project_detail_other_user_public_success(client):
    u_owner = client.post(
        "/api/v1/auth/register",
        json={"username": "pubowner", "email": "pubowner@example.com", "password": "Password123!"}
    ).json()
    u_other = client.post(
        "/api/v1/auth/register",
        json={"username": "pubother", "email": "pubother@example.com", "password": "Password123!"}
    ).json()

    create_res = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {u_owner['access_token']}"},
        json={"name": "Public Shared Project", "visibility": "PUBLIC"}
    )
    project_id = create_res.json()["id"]

    response = client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {u_other['access_token']}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == project_id
    assert response.json()["name"] == "Public Shared Project"

def test_get_project_detail_other_user_private_returns_404(client):
    u_owner = client.post(
        "/api/v1/auth/register",
        json={"username": "privowner", "email": "privowner@example.com", "password": "Password123!"}
    ).json()
    u_other = client.post(
        "/api/v1/auth/register",
        json={"username": "privother", "email": "privother@example.com", "password": "Password123!"}
    ).json()

    create_res = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {u_owner['access_token']}"},
        json={"name": "Secret Private Project", "visibility": "PRIVATE"}
    )
    project_id = create_res.json()["id"]

    response = client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {u_other['access_token']}"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_get_project_detail_nonexistent_uuid(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "nonexistuser", "email": "nonexist@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/projects/{fake_id}", headers=headers)
    assert response.status_code == 404

def test_get_project_detail_invalid_uuid(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "invuuiduser", "email": "invuuid@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    response = client.get("/api/v1/projects/not-a-valid-uuid", headers=headers)
    assert response.status_code == 422

def test_get_project_detail_unauthenticated(client):
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/projects/{fake_id}")
    assert response.status_code == 401


# --- PATCH /api/v1/projects/{project_id} Tests ---

def test_update_project_name_and_slug_regeneration(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "updnameuser", "email": "updname@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    create_res = client.post("/api/v1/projects", headers=headers, json={"name": "Initial Name"})
    project_id = create_res.json()["id"]
    assert create_res.json()["slug"] == "initial-name"

    response = client.patch(
        f"/api/v1/projects/{project_id}",
        headers=headers,
        json={"name": "Brand New Name"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Brand New Name"
    assert data["slug"] == "brand-new-name"

def test_update_project_description_only(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "upddescuser", "email": "upddesc@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    create_res = client.post("/api/v1/projects", headers=headers, json={"name": "Retain Slug Workspace", "description": "Old desc"})
    project_id = create_res.json()["id"]

    response = client.patch(
        f"/api/v1/projects/{project_id}",
        headers=headers,
        json={"description": "Newly updated desc"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Retain Slug Workspace"
    assert data["slug"] == "retain-slug-workspace"
    assert data["description"] == "Newly updated desc"

def test_update_project_visibility_only(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "updvisuser", "email": "updvis@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    create_res = client.post("/api/v1/projects", headers=headers, json={"name": "Visibility Toggle", "visibility": "PRIVATE"})
    project_id = create_res.json()["id"]

    response = client.patch(
        f"/api/v1/projects/{project_id}",
        headers=headers,
        json={"visibility": "PUBLIC"}
    )
    assert response.status_code == 200
    assert response.json()["visibility"] == "PUBLIC"

def test_update_project_multiple_fields(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "updmultiuser", "email": "updmulti@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    create_res = client.post("/api/v1/projects", headers=headers, json={"name": "Old Mult", "visibility": "PRIVATE"})
    project_id = create_res.json()["id"]

    response = client.patch(
        f"/api/v1/projects/{project_id}",
        headers=headers,
        json={"name": "New Mult", "description": "New Desc", "visibility": "PUBLIC"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Mult"
    assert data["slug"] == "new-mult"
    assert data["description"] == "New Desc"
    assert data["visibility"] == "PUBLIC"

def test_update_project_non_owner_attempt(client):
    u_owner = client.post(
        "/api/v1/auth/register",
        json={"username": "updowner", "email": "updowner@example.com", "password": "Password123!"}
    ).json()
    u_other = client.post(
        "/api/v1/auth/register",
        json={"username": "updother", "email": "updother@example.com", "password": "Password123!"}
    ).json()

    pub_res = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {u_owner['access_token']}"},
        json={"name": "Public Project", "visibility": "PUBLIC"}
    )
    pub_id = pub_res.json()["id"]

    res_forbidden = client.patch(
        f"/api/v1/projects/{pub_id}",
        headers={"Authorization": f"Bearer {u_other['access_token']}"},
        json={"name": "Hacked Name"}
    )
    assert res_forbidden.status_code == 403

    priv_res = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {u_owner['access_token']}"},
        json={"name": "Private Project", "visibility": "PRIVATE"}
    )
    priv_id = priv_res.json()["id"]

    res_notfound = client.patch(
        f"/api/v1/projects/{priv_id}",
        headers={"Authorization": f"Bearer {u_other['access_token']}"},
        json={"name": "Hacked Name"}
    )
    assert res_notfound.status_code == 404

def test_update_project_nonexistent_uuid(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "updnonexist", "email": "updnonexist@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    fake_id = str(uuid.uuid4())
    response = client.patch(f"/api/v1/projects/{fake_id}", headers=headers, json={"name": "New Name"})
    assert response.status_code == 404

def test_update_project_invalid_uuid(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "updinvuuid", "email": "updinvuuid@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    response = client.patch("/api/v1/projects/not-a-valid-uuid", headers=headers, json={"name": "New Name"})
    assert response.status_code == 422

def test_update_project_unauthenticated(client):
    fake_id = str(uuid.uuid4())
    response = client.patch(f"/api/v1/projects/{fake_id}", json={"name": "New Name"})
    assert response.status_code == 401

@pytest.mark.parametrize(
    "payload",
    [
        {"name": "   "},                             # Whitespace only
        {"name": "a" * 151},                       # Name too long
        {"description": "d" * 501},                # Description too long
        {"visibility": "INVALID_VISIBILITY"},      # Invalid enum
    ]
)
def test_update_project_validation_failures(client, payload):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "updvaluser", "email": "updval@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    create_res = client.post("/api/v1/projects", headers=headers, json={"name": "Valid Base Project"})
    project_id = create_res.json()["id"]

    response = client.patch(f"/api/v1/projects/{project_id}", headers=headers, json=payload)
    assert response.status_code == 422


# --- DELETE /api/v1/projects/{project_id} Tests ---

def test_delete_project_owner_success(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "delowner", "email": "delowner@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    create_res = client.post("/api/v1/projects", headers=headers, json={"name": "Project To Delete"})
    project_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/projects/{project_id}", headers=headers)
    assert del_res.status_code == 204
    assert del_res.content == b""

    get_res = client.get(f"/api/v1/projects/{project_id}", headers=headers)
    assert get_res.status_code == 404

def test_delete_project_nonexistent_uuid(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "delnonexist", "email": "delnonexist@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    fake_id = str(uuid.uuid4())
    response = client.delete(f"/api/v1/projects/{fake_id}", headers=headers)
    assert response.status_code == 404

def test_delete_project_non_owner_attempts(client):
    u_owner = client.post(
        "/api/v1/auth/register",
        json={"username": "delrealowner", "email": "delrealowner@example.com", "password": "Password123!"}
    ).json()
    u_other = client.post(
        "/api/v1/auth/register",
        json={"username": "delotheruser", "email": "delotheruser@example.com", "password": "Password123!"}
    ).json()

    pub_res = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {u_owner['access_token']}"},
        json={"name": "Public Project Delete", "visibility": "PUBLIC"}
    )
    pub_id = pub_res.json()["id"]

    res_forbidden = client.delete(
        f"/api/v1/projects/{pub_id}",
        headers={"Authorization": f"Bearer {u_other['access_token']}"}
    )
    assert res_forbidden.status_code == 403

    priv_res = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {u_owner['access_token']}"},
        json={"name": "Private Project Delete", "visibility": "PRIVATE"}
    )
    priv_id = priv_res.json()["id"]

    res_notfound = client.delete(
        f"/api/v1/projects/{priv_id}",
        headers={"Authorization": f"Bearer {u_other['access_token']}"}
    )
    assert res_notfound.status_code == 404

def test_delete_project_invalid_uuid(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "delinvuuid", "email": "delinvuuid@example.com", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    response = client.delete("/api/v1/projects/invalid-uuid-str", headers=headers)
    assert response.status_code == 422

def test_delete_project_unauthenticated(client):
    fake_id = str(uuid.uuid4())
    response = client.delete(f"/api/v1/projects/{fake_id}")
    assert response.status_code == 401



