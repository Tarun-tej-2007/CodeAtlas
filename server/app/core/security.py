from fastapi import HTTPException, status

class InvalidTokenError(HTTPException):
    """
    Raised when a JWT token signature validation fails, token type is invalid, or parsing errors occur.
    """
    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class ExpiredTokenError(HTTPException):
    """
    Raised when a JWT token expiration time (exp) has passed.
    """
    def __init__(self, detail: str = "Signature has expired") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class InvalidCredentialsError(HTTPException):
    """
    Raised during authentication flows if username/email lookups fail or password verification fails.
    """
    def __init__(self, detail: str = "Incorrect email or password") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
