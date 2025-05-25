# test_auth.py

from fastapi import status
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.user import User
from app.core.security import get_password_hash


def test_login(client: TestClient, test_db: Session):
    # Create a test user
    hashed_password = get_password_hash("test_password")

    test_user = User(username="test_user_login", hashed_password=hashed_password)
    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)

    # Login attempt
    # For OAuth2PasswordRequestForm, FastAPI expects form data, not JSON.
    # TestClient's `data` parameter sends it as form data.
    login_data = {"username": "test_user_login", "password": "test_password"}
    response = client.post("/auth/login/token", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"


# Ensure two blank lines before this function
def test_login_wrong_password(client: TestClient, test_db: Session):
    # Create a test user
    hashed_password = get_password_hash("test_password_wrong")
    test_user = User(username="test_user_wrong_pass", hashed_password=hashed_password)
    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)

    # Login attempt with incorrect password
    login_data = {"username": "test_user_wrong_pass", "password": "incorrect_password"}
    response = client.post("/auth/login/token", data=login_data)   # Corrected path

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Ensure two blank lines before this function
def test_login_nonexistent_user(client: TestClient):
    # Login attempt with incorrect user
    login_data = {"username": "nonexistent_user_test", "password": "any_password"}
    response = client.post("/auth/login/token", data=login_data)   # Corrected path

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
