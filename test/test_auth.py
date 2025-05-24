import pytest
from fastapi import status
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

# It's good practice to import models and utility functions at the top
from app.models.user import User # Make sure your User model is correctly imported
from app.core.security import get_password_hash, create_access_token # For test setup
# from app.api.schemas import UserCreate, TodoCreate # Uncomment if used directly

# Note: The 'client' and 'test_db' fixtures are provided by your conftest.py

def test_login(client: TestClient, test_db: Session):
    # Create a test user
    hashed_password = get_password_hash("test_password")
    # REMOVED 'email' argument to avoid TypeError if User model doesn't accept it directly.
    # If your User model *does* have an email field and you want to set it here,
    # ensure the model's __init__ or SQLAlchemy's default constructor handles it.
    # For now, we assume the API endpoint for user creation (/auth/signup or /users/)
    # handles email via Pydantic schemas.
    test_user = User(
        username="test_user_login",
        hashed_password=hashed_password
    )
    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)

    # Login attempt
    login_data = {"username": "test_user_login", "password": "test_password"}
    response = client.post("/auth/login", data=login_data) # Path confirmed as /auth/login

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient, test_db: Session):
    # Create a test user
    hashed_password = get_password_hash("test_password_wrong")
    # REMOVED 'email' argument
    test_user = User(
        username="test_user_wrong_pass",
        hashed_password=hashed_password
    )
    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)

    # Login attempt with incorrect password
    login_data = {"username": "test_user_wrong_pass", "password": "incorrect_password"}
    response = client.post("/auth/login", data=login_data) # Path confirmed as /auth/login

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_nonexistent_user(client: TestClient): # No test_db needed if not creating a user
    # Login attempt with incorrect user
    login_data = {"username": "nonexistent_user_test", "password": "any_password"}
    response = client.post("/auth/login", data=login_data) # Path confirmed as /auth/login

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

