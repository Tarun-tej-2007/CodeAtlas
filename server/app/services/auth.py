from typing import Any
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.user import User
from app.repositories.user import UserRepository
from app.core.password import PasswordService
from app.core.jwt import JWTService, TokenType
from app.core.config import settings
from app.services.redis import RedisService
from app.core.exceptions import (
    InvalidCredentialsError,
    InactiveUserError,
    InvalidTokenError,
    UserNotFoundError,
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    RegistrationFailedError,
)

class AuthService:
    """
    Business logic service for handling platform authentication operations.
    Integrates password operations, JWT claims management, and database state retrieval.
    """

    def __init__(
        self,
        db: Session,
        user_repo: UserRepository | None = None,
        redis_service: RedisService | None = None,
    ) -> None:
        self.db = db
        self.user_repo = user_repo or UserRepository(db)
        self.redis_service = redis_service or RedisService()

    def hash_password(self, password: str) -> str:
        """
        Hashes a raw password string using the configured PasswordService.
        """
        return PasswordService.hash_password(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verifies a raw password string against its stored hash.
        """
        return PasswordService.verify_password(password, hashed_password)

    def _validate_user_active(self, user: User) -> None:
        """
        Verifies if the user profile is active, raising InactiveUserError if deactivated.
        """
        if not user.is_active:
            raise InactiveUserError("User account is deactivated")

    def authenticate_user(self, login_identifier: str, password: str) -> User:
        """
        Authenticates a user via email or username against their stored password hash.
        Throws domain-specific exceptions on mismatch or inactive account profiles.
        """
        user = self.user_repo.get_by_identifier(login_identifier)

        if not user or not self.verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Incorrect email/username or password")

        self._validate_user_active(user)

        return user

    def create_access_token(self, user_id: uuid.UUID) -> str:
        """
        Generates a signed JWT access token for the user.
        """
        return JWTService.create_access_token(subject=user_id)

    def create_refresh_token(self, user_id: uuid.UUID) -> str:
        """
        Generates a signed JWT refresh token for the user.
        """
        return JWTService.create_refresh_token(subject=user_id)

    def decode_and_validate_token(self, token: str, expected_type: TokenType) -> dict[str, Any]:
        """
        Decodes and verifies a JWT token scope and signature, converting library exceptions to domain ones.
        """
        try:
            return JWTService.decode_token(token, expected_type=expected_type)
        except Exception as e:
            raise InvalidTokenError("Invalid token or signature has expired") from e

    def get_authenticated_user(self, token: str) -> User:
        """
        Validates an access token and retrieves the corresponding User from the database.
        Throws domain-specific exceptions if token is invalid or user record does not exist.
        """
        payload = self.decode_and_validate_token(token, expected_type=TokenType.ACCESS)
        subject = payload.get("sub")
        
        if not subject:
            raise InvalidTokenError("Could not validate credentials")

        try:
            user_id = uuid.UUID(subject)
        except ValueError as e:
            raise InvalidTokenError("Malformed user credentials") from e

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")

        self._validate_user_active(user)

        return user

    def register(
        self,
        username: str,
        email: str,
        password: str,
    ) -> dict[str, Any]:
        """
        Registers a new user on the platform.
        Coordinates validation, transaction-safe persistence, and authentication token issuance.
        """
        # Check whether email already exists
        if self.user_repo.exists_by_email(email):
            raise EmailAlreadyExistsError("Email is already registered")

        # Check whether username already exists
        if self.user_repo.exists_by_username(username):
            raise UsernameAlreadyExistsError("Username is already taken")

        # Hash password using existing password service
        password_hash = self.hash_password(password)

        # Create the User entity
        user = User(
            email=email,
            username=username,
            password_hash=password_hash,
        )

        # Persist the user transactionally
        try:
            self.user_repo.create(user)
            self.db.commit()
            self.db.refresh(user)
        except IntegrityError as e:
            self.db.rollback()
            # Double check database constraints under concurrency
            if self.user_repo.exists_by_email(email):
                raise EmailAlreadyExistsError("Email is already registered") from e
            if self.user_repo.exists_by_username(username):
                raise UsernameAlreadyExistsError("Username is already taken") from e
            raise RegistrationFailedError("Database save failed during registration") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RegistrationFailedError("Registration failed due to a database error") from e

        # Generate JWT tokens after a successful database commit
        access_token = self.create_access_token(user.id)
        refresh_token = self.create_refresh_token(user.id)

        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }

    def login(self, identifier: str, password: str) -> dict[str, Any]:
        """
        Authenticates a user by email/username and issues new JWT access and refresh tokens.
        """
        # Call the existing authenticate_user (it handles checks, verification, and active state)
        user = self.authenticate_user(identifier, password)

        # Generate tokens
        access_token = self.create_access_token(user.id)
        refresh_token = self.create_refresh_token(user.id)

        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }

    def get_current_user_profile(self, user_id: uuid.UUID) -> User:
        """
        Retrieves the profile of the currently authenticated user by ID.
        Ensures the user exists and is active.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")

        self._validate_user_active(user)

        return user

    def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """
        Validates a refresh token and generates a new short-lived access token.
        """
        # Decode and validate refresh token (ensures signature, expiration, and TokenType.REFRESH)
        payload = self.decode_and_validate_token(refresh_token, expected_type=TokenType.REFRESH)
        
        jti = payload.get("jti")
        if not jti:
            raise InvalidTokenError("Missing JWT ID claim")

        # Assert token is not revoked in Redis
        if self.redis_service.is_token_revoked(jti):
            raise InvalidTokenError("Token has been revoked")

        subject = payload.get("sub")

        if not subject:
            raise InvalidTokenError("Could not validate credentials")

        try:
            user_id = uuid.UUID(subject)
        except ValueError as e:
            raise InvalidTokenError("Malformed user credentials") from e

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")

        self._validate_user_active(user)

        # Generate a new access token
        access_token = self.create_access_token(user.id)

        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    def logout(self, refresh_token: str) -> None:
        """
        Invalidates a refresh token by adding its JTI to the Redis blocklist.
        """
        # Decode, verify signature, expiration, and REFRESH token type
        payload = self.decode_and_validate_token(refresh_token, expected_type=TokenType.REFRESH)

        jti = payload.get("jti")
        if not jti:
            raise InvalidTokenError("Missing JWT ID claim")

        # Idempotency check: if already revoked, exit silently
        if self.redis_service.is_token_revoked(jti):
            return

        exp = payload.get("exp")
        if not exp:
            raise InvalidTokenError("Missing token expiration claim")

        # Calculate remaining lifetime in seconds
        now_epoch = int(datetime.now(timezone.utc).timestamp())
        expires_in = exp - now_epoch

        # Store the token ID in Redis with TTL matching remaining lifetime
        self.redis_service.revoke_token(jti, expires_in)







