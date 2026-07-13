import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.auth import AuthService
from app.schemas.auth import (
    UserRegister,
    AuthResponse,
    UserLogin,
    CurrentUserResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
)
from app.core.dependencies import get_current_user
from app.core.exceptions import (
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    RegistrationFailedError,
    InvalidCredentialsError,
    InactiveUserError,
    UserNotFoundError,
    InvalidTokenError,
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

@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate an existing user",
    description="Authenticates the user with username/email and password, returning tokens."
)
def login(
    data: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    Handles user login request.
    Translates backend domain exceptions into standard HTTP exception payloads.
    """
    auth_service = AuthService(db)
    try:
        return auth_service.login(
            identifier=data.identifier,
            password=data.password,
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
        )
    except InactiveUserError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e) or "User account is deactivated",
        )

@router.get(
    "/me",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve current user profile",
    description="Returns the profile details of the currently authenticated user."
)
def get_me(
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    HTTP endpoint to retrieve the current user profile.
    Translates domain-specific errors (UserNotFoundError, InactiveUserError) into standard HTTP responses.
    """
    auth_service = AuthService(db)
    try:
        return auth_service.get_current_user_profile(current_user_id)

    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e) or "User not found",
        )
    except InactiveUserError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e) or "User account is deactivated",
        )

@router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Acquire a new access token",
    description="Validates a refresh token and returns a newly generated access token."
)
def refresh(
    data: TokenRefreshRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Handles refresh token request.
    Translates backend domain exceptions into standard HTTP exception payloads.
    """
    auth_service = AuthService(db)
    try:
        return auth_service.refresh_token(data.refresh_token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e) or "Invalid token or signature has expired",
        )
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e) or "User not found",
        )
    except InactiveUserError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e) or "User account is deactivated",
        )

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout a user session",
    description="Invalidates the provided refresh token by adding its JTI to the Redis blocklist."
)
def logout(
    data: TokenRefreshRequest,
    db: Session = Depends(get_db)
) -> None:
    """
    Handles user logout request.
    Invalidates the refresh token and returns HTTP 204 No Content.
    """
    auth_service = AuthService(db)
    try:
        auth_service.logout(data.refresh_token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e) or "Invalid token or signature has expired",
        )





