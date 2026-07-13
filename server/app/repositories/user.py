import uuid
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:
    """
    SQLAlchemy 2.0 repository mapping database queries for the User model.
    Encapsulates all SQL statements to isolate the service layer from direct database queries.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """
        Retrieves a User by their unique UUID primary key.
        """
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        """
        Retrieves a User by their unique email address.
        """
        statement = select(User).where(User.email == email)
        return self.db.scalar(statement)

    def get_by_username(self, username: str) -> User | None:
        """
        Retrieves a User by their unique username.
        """
        statement = select(User).where(User.username == username)
        return self.db.scalar(statement)

    def get_by_identifier(self, identifier: str) -> User | None:
        """
        Retrieves a User by either their email address or username in a single query.
        """
        statement = select(User).where(
            or_(User.email == identifier, User.username == identifier)
        )
        return self.db.scalar(statement)

    def create(self, user: User) -> User:
        """
        Adds a new User entity to the database session and flushes it to populate generated fields.
        """
        self.db.add(user)
        self.db.flush()
        return user

    def exists_by_email(self, email: str) -> bool:
        """
        Checks if a user with the given email address exists.
        """
        statement = select(User.id).where(User.email == email)
        return self.db.scalar(statement) is not None

    def exists_by_username(self, username: str) -> bool:
        """
        Checks if a user with the given username exists.
        """
        statement = select(User.id).where(User.username == username)
        return self.db.scalar(statement) is not None

