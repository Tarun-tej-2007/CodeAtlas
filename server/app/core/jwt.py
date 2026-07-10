from datetime import datetime, timedelta, timezone
import enum
from typing import Any
import uuid
import jwt

from app.core.config import settings
from app.core.security import InvalidTokenError, ExpiredTokenError

class TokenType(str, enum.Enum):
    """
    Enumerates valid token scopes to prevent refresh tokens from being reused as access tokens.
    """
    ACCESS = "access"
    REFRESH = "refresh"

class JWTService:
    """
    Reusable utility service for managing JSON Web Tokens (JWT).
    
    JWT Claims Strategy (RFC 7519):
    - sub (subject): Identifies the user ID (UUID) that owns the token scope.
    - exp (expiration time): Restricts token validity windows to minimize hijack windows.
    - iat (issued at): Audits token age.
    - iss (issuer): Authenticates signature origin (loaded from settings.JWT_ISSUER).
    - aud (audience): Restrains target resource consumption scope (loaded from settings.JWT_AUDIENCE).
    - jti (JWT ID): Unique UUID v4 token identifier to block replay attacks in future blacklists.
    - token_type: Custom claim ("access" or "refresh") to restrict usage scope.
    
    Refresh Tokens vs Access Tokens:
    - Access Tokens are short-lived and optimized for rapid stateless checks.
    - Refresh Tokens are long-lived and used only at `/refresh` endpoints to
      issue new access tokens. Decoupling scopes prevents refresh tokens from accessing API routes.
    """

    @classmethod
    def create_access_token(cls, subject: uuid.UUID | str) -> str:
        """
        Generates a short-lived access token containing user identity and scopes.
        """
        now = datetime.now(timezone.utc)
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(subject),
            "iat": now,
            "exp": now + expires_delta,
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
            "jti": str(uuid.uuid4()),
            "token_type": TokenType.ACCESS.value,
        }
        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @classmethod
    def create_refresh_token(cls, subject: uuid.UUID | str) -> str:
        """
        Generates a long-lived refresh token to acquire new access tokens.
        """
        now = datetime.now(timezone.utc)
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": str(subject),
            "iat": now,
            "exp": now + expires_delta,
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
            "jti": str(uuid.uuid4()),
            "token_type": TokenType.REFRESH.value,
        }
        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @classmethod
    def decode_token(cls, token: str, expected_type: TokenType) -> dict[str, Any]:
        """
        Decodes a JWT string, validating its signature, expiration, type, issuer, and audience.
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                issuer=settings.JWT_ISSUER,
                audience=settings.JWT_AUDIENCE,
            )
            # Verify matching token type
            if payload.get("token_type") != expected_type.value:
                raise InvalidTokenError(detail=f"Invalid token scope: expected '{expected_type.value}'")
            return payload
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenError()
        except jwt.PyJWTError:
            raise InvalidTokenError()
