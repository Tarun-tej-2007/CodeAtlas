import pytest
import uuid
from datetime import datetime
from pydantic import ValidationError
from app.models.user import User
from app.models.project import Project
from app.models.enums import ProjectVisibility
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.repositories.project import ProjectRepository
from app.services.project import ProjectService
from app.core.exceptions import ProjectNotFoundError

# --- 1. Model & Relationship Tests ---

def test_project_model_creation_and_relationship(db_session):
    # Create owner
    owner = User(
        username="projectowner",
        email="owner@example.com",
        password_hash="hashed_pw"
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)

    # Create project
    project = Project(
        owner_id=owner.id,
        name="Test Workspace",
        slug="test-workspace",
        description="A test workspace",
        visibility=ProjectVisibility.PRIVATE
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    assert project.id is not None
    assert project.owner_id == owner.id
    assert project.name == "Test Workspace"
    assert project.slug == "test-workspace"
    assert project.description == "A test workspace"
    assert project.visibility == ProjectVisibility.PRIVATE
    assert isinstance(project.created_at, datetime)
    assert isinstance(project.updated_at, datetime)

    # Verify relationship from Owner back to Project
    assert len(owner.projects) == 1
    assert owner.projects[0].id == project.id

    # Cascade delete check
    db_session.delete(owner)
    db_session.commit()

    # Project should be cascade deleted
    db_proj = db_session.get(Project, project.id)
    assert db_proj is None

# --- 2. Schema Validation Tests ---

def test_project_create_schema_validation():
    # Valid schema payload
    data = ProjectCreate(name="  CodeAtlas Project  ", description="Simple description")
    assert data.name == "CodeAtlas Project"  # Whitespace trimmed
    assert data.description == "Simple description"
    assert data.visibility == ProjectVisibility.PRIVATE  # Default visibility

    # Empty name
    with pytest.raises(ValidationError):
        ProjectCreate(name="")

    # Whitespace-only name
    with pytest.raises(ValidationError):
        ProjectCreate(name="     ")

    # Name too long (> 150)
    with pytest.raises(ValidationError):
        ProjectCreate(name="a" * 151)

    # Description too long (> 500)
    with pytest.raises(ValidationError):
        ProjectCreate(name="Valid Name", description="d" * 501)

def test_project_update_schema_validation():
    # Partial updates
    upd = ProjectUpdate(description="Updated description")
    assert upd.description == "Updated description"
    assert upd.name is None

    # Empty/whitespace name updates should fail
    with pytest.raises(ValidationError):
        ProjectUpdate(name="   ")

# --- 3. Repository Layer Tests ---

def test_project_repository_crud(db_session):
    # Setup owner
    owner = User(username="repoowner", email="repo@example.com", password_hash="pw")
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)

    repo = ProjectRepository(db_session)

    # 1. Create
    proj = Project(
        owner_id=owner.id,
        name="Repository Project",
        slug="repository-project",
        description="Repo description",
        visibility=ProjectVisibility.PUBLIC
    )
    repo.create(proj)
    db_session.commit()

    # 2. Get by ID
    fetched = repo.get_by_id(proj.id)
    assert fetched is not None
    assert fetched.name == "Repository Project"

    # 3. Get by slug
    fetched_slug = repo.get_by_slug(owner.id, "repository-project")
    assert fetched_slug is not None
    assert fetched_slug.id == proj.id

    # 4. Slug exists check
    assert repo.slug_exists(owner.id, "repository-project") is True
    assert repo.slug_exists(owner.id, "nonexistent-slug") is False

    # 5. List by owner
    projs = repo.list_by_owner(owner.id)
    assert len(projs) == 1
    assert projs[0].id == proj.id

    # 6. Update
    proj.description = "New description"
    repo.update(proj)
    db_session.commit()
    db_session.refresh(proj)
    assert proj.description == "New description"

    # 7. Delete
    repo.delete(proj)
    db_session.commit()
    assert repo.get_by_id(proj.id) is None

# --- 4. Service Layer & Slug Generation Tests ---

def test_project_service_slug_generation_and_crud(db_session):
    # Setup owner
    owner = User(username="servowner", email="serv@example.com", password_hash="pw")
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)

    service = ProjectService(db_session)

    # 1. Create Project (slug generation)
    data1 = ProjectCreate(name="  CodeAtlas Platform !!! ", description="Core platform project")
    p1 = service.create_project(owner.id, data1)
    
    assert p1.slug == "codeatlas-platform"
    assert p1.name == "CodeAtlas Platform !!!"

    # 2. Duplicate name (slug incrementing)
    data2 = ProjectCreate(name="CodeAtlas Platform")
    p2 = service.create_project(owner.id, data2)
    assert p2.slug == "codeatlas-platform-2"

    # 3. Third duplicate
    data3 = ProjectCreate(name="CodeAtlas Platform")
    p3 = service.create_project(owner.id, data3)
    assert p3.slug == "codeatlas-platform-3"

    # 4. Get Project
    fetched = service.get_project(p1.id)
    assert fetched.id == p1.id

    # Get non-existent
    with pytest.raises(ProjectNotFoundError):
        service.get_project(uuid.uuid4())

    # 5. List Projects
    lst = service.list_projects(owner.id)
    assert len(lst) == 3

    # 6. Update name (regenerates slug)
    update_data = ProjectUpdate(name="Updated Platform name")
    p1_updated = service.update_project(p1.id, update_data)
    assert p1_updated.name == "Updated Platform name"
    assert p1_updated.slug == "updated-platform-name"

    # Update description only (retains slug)
    update_desc = ProjectUpdate(description="Updated desc only")
    p1_updated = service.update_project(p1.id, update_desc)
    assert p1_updated.slug == "updated-platform-name"
    assert p1_updated.description == "Updated desc only"

    # 7. Delete Project
    service.delete_project(p1.id)
    with pytest.raises(ProjectNotFoundError):
        service.get_project(p1.id)
