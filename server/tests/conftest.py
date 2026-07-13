import pytest
from unittest.mock import MagicMock
import sys
import os

# Add server directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set environment variables for testing before loading settings
os.environ["SECRET_KEY"] = "test-secret-key-12345-test-secret-key-12345"
# Reuses postgresql schema during engine load to prevent SQLite pool config arguments error
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/codeatlas"

# Mock Redis client before importing app
import redis
mock_redis = MagicMock()
redis_store = {}

def mock_setex(name, time, value):
    redis_store[name] = value

def mock_exists(name):
    return name in redis_store

mock_redis.setex.side_effect = mock_setex
mock_redis.exists.side_effect = mock_exists

# Patch redis.from_url to return our mock_redis client globally
redis.from_url = MagicMock(return_value=mock_redis)

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db

# Create SQLite engine for testing
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)

@pytest.fixture(name="db_session")
def db_session_fixture():
    """
    Creates isolated test database tables, yields session, and cleans up.
    """
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(autouse=True)
def clear_redis_store():
    """
    Automatically clears the mock Redis blocklist store before each test.
    """
    redis_store.clear()

@pytest.fixture(name="client")
def client_fixture(db_session):
    """
    Configures TestClient overriding DB dependency.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
