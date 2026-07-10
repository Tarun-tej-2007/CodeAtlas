class AuthError(Exception):
    """
    Base authentication exception class for all security and token operations.
    """
    pass

class InvalidCredentialsError(AuthError):
    """
    Raised when email/username matches fail or password hashes do not match.
    """
    pass

class InactiveUserError(AuthError):
    """
    Raised when an authenticated user profile is marked as deactivated.
    """
    pass

class InvalidTokenError(AuthError):
    """
    Raised when JWT signature verification, type assertion, or parsing fails.
    """
    pass

class UserNotFoundError(AuthError):
    """
    Raised when a user UUID primary key lookup fails to return any DB record.
    """
    pass
