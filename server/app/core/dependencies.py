import uuid
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.jwt import JWTService, TokenType
from app.core.security import InvalidTokenError

# Configure OAuth2PasswordBearer flow mapping to future login endpoints
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login",
    auto_error=True,
)

def get_current_user(token: str = Depends(oauth2_scheme)) -> uuid.UUID:
    """
    FastAPI dependency that decodes, validates, and extracts the current
    authenticated user's ID from an active access token.
    
    Does not run database queries, simplifying downstream service isolation.
    """
    payload = JWTService.decode_token(token, expected_type=TokenType.ACCESS)
    subject = payload.get("sub")
    
    if not subject:
        raise InvalidTokenError()
        
    try:
        return uuid.UUID(subject)
    except ValueError:
        raise InvalidTokenError(detail="Malformed user identification credentials")
