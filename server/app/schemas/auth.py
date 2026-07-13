import uuid
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict, EmailStr

class UserRegister(BaseModel):
    """
    Pydantic schema validating user registration input parameters.
    """
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Letters, numbers and underscores only."
    )
    email: EmailStr = Field(
        ...,
        description="Valid email format."
    )
    password: str = Field(
        ...,
        description="Password meeting security criteria."
    )

    @field_validator("email", mode="after")
    @classmethod
    def normalize_email(cls, v: EmailStr) -> str:
        """
        Normalizes the email to lowercase before database persistence.
        """
        return str(v).lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Enforces password complexity constraints:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

class UserResponse(BaseModel):
    """
    Pydantic schema mapping the user entity representation for responses.
    """
    id: uuid.UUID
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)

class AuthResponse(BaseModel):
    """
    Pydantic schema mapping tokens and user profile after authentication/registration.
    """
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

class UserLogin(BaseModel):
    """
    Pydantic schema validating user login request credentials.
    """
    identifier: str = Field(
        ...,
        min_length=1,
        description="Username or email address."
    )
    password: str = Field(
        ...,
        min_length=1,
        description="User password."
    )

    @field_validator("identifier")
    @classmethod
    def trim_identifier(cls, v: str) -> str:
        """
        Trims leading and trailing whitespace from the username/email identifier.
        """
        trimmed = v.strip() if v else ""
        if not trimmed:
            raise ValueError("Identifier must not be empty or whitespace only")
        return trimmed

    @field_validator("password")
    @classmethod
    def non_empty_password(cls, v: str) -> str:
        """
        Ensures password is not empty.
        """
        if not v:
            raise ValueError("Password must not be empty")
        return v

class CurrentUserResponse(BaseModel):
    """
    Pydantic schema representing the current user profile response.
    Exposes only safe public profile parameters.
    """
    id: uuid.UUID
    username: str
    email: EmailStr
    full_name: str | None = Field(default=None, description="User full name.")
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


