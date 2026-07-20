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

class EmailAlreadyExistsError(AuthError):
    """
    Raised when user tries to register with an email that is already registered.
    """
    pass

class UsernameAlreadyExistsError(AuthError):
    """
    Raised when user tries to register with a username that is already registered.
    """
    pass

class RegistrationFailedError(AuthError):
    """
    Raised when a general database or persistence operation failure occurs during registration.
    """
    pass

class ProjectNotFoundError(Exception):
    """
    Raised when a project UUID lookup fails.
    """
    pass

class ProjectForbiddenError(Exception):
    """
    Raised when an authenticated user attempts to modify or delete a project they do not own.
    """
    pass



