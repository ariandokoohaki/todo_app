# test/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine # Not strictly needed here if engine is imported
from sqlalchemy.orm import sessionmaker # Not strictly needed here if SessionLocal is imported

from app.main import app # <--- Correctly imports the app from main.py
from app.core.database import Base, SessionLocal, engine # Assuming engine is configured for tests
from app.api.dependencies import get_db

# IMPORTANT: Import your models so their tables are registered with SQLAlchemy's metadata
from app.models.user import User
from app.models.todo import Todo # Make sure this is uncommented if you have it

@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_db():
    connection = engine.connect()
    transaction = connection.begin()
    db = SessionLocal(bind=connection) # Uses SessionLocal from your app.core.database

    yield db

    db.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def override_get_db(test_db): # Renamed fixture for clarity that it provides the override mechanism
    def _override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    yield # This yield allows the setup (override) and teardown (clear)
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def client(override_get_db): # Depends on the override_get_db fixture to apply the override
    with TestClient(app) as c: # TestClient uses the app with overrides
        yield c
