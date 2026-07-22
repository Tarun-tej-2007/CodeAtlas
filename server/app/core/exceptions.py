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


class AnalysisEngineError(Exception):
    """Base exception for all Analysis Engine communication errors."""
    pass


class AnalysisEngineConnectionError(AnalysisEngineError):
    """Raised when connecting to the Analysis Engine fails."""
    pass


class AnalysisEngineTimeoutError(AnalysisEngineError):
    """Raised when a request to the Analysis Engine times out."""
    pass


class AnalysisEngineRequestError(AnalysisEngineError):
    """Raised when the Analysis Engine returns a client/request error (4xx)."""
    pass




