import sys
import os
import uuid

# Add the server directory to sys.path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import SessionLocal
from app.services.auth import AuthService
from app.services.project import ProjectService
from app.schemas.project import ProjectCreate
from app.core.exceptions import EmailAlreadyExistsError, UsernameAlreadyExistsError
from app.models.enums import ProjectVisibility

def seed():
    db = SessionLocal()
    auth_service = AuthService(db)
    project_service = ProjectService(db)
    
    username = "devuser"
    email = "dev@codeatlas.local"
    password = "devpassword123!"
    
    print("Seeding database...")
    
    # Register or login user
    try:
        result = auth_service.register(
            username=username,
            email=email,
            password=password
        )
        user = result["user"]
        token = result["access_token"]
        print(f"Created new user: {email}")
    except (EmailAlreadyExistsError, UsernameAlreadyExistsError):
        print(f"User {email} already exists. Logging in...")
        result = auth_service.login(identifier=email, password=password)
        user = result["user"]
        token = result["access_token"]
        
    print("\n--- DEV TOKEN ---")
    print(token)
    print("-----------------\n")

    # Create a sample project if none exists
    projects = project_service.list_projects_paginated(
        owner_id=user.id,
        page=1,
        size=10
    )
    
    if projects.total == 0:
        print("Creating a mock project for devuser...")
        project_data = ProjectCreate(
            name="Frontend Service",
            description="Main web interface for CodeAtlas",
            visibility=ProjectVisibility.PRIVATE
        )
        project_service.create_project(
            owner_id=user.id,
            data=project_data
        )
        
        project_data2 = ProjectCreate(
            name="Analysis Engine",
            description="Python based static analysis service",
            visibility=ProjectVisibility.PRIVATE
        )
        project_service.create_project(
            owner_id=user.id,
            data=project_data2
        )
        print("Mock projects created successfully.")
    else:
        print("Mock projects already exist.")
        
    db.close()

if __name__ == "__main__":
    seed()
