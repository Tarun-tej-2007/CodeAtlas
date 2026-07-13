from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.auth import AuthService
from app.schemas.auth import UserRegister, AuthResponse
from app.core.exceptions import (
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    RegistrationFailedError,
)

router = APIRouter()

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Validates user registration, persists the user, and returns access and refresh tokens."
)
def register(
    data: UserRegister,
    db: Session = Depends(get_db)
) -> Any:
    """
    Handles user registration request.
    Translates backend domain exceptions into standard HTTP exception payloads.
    """
    auth_service = AuthService(db)
    try:
        return auth_service.register(
            username=data.username,
            email=data.email,
            password=data.password,
        )
    except EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except UsernameAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except RegistrationFailedError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

