from fastapi import status
from sqlalchemy.orm import Session  # Added for type hinting if not already there

# Assuming these are correctly defined
from app.api.schemas import UserCreate
from app.core.security import get_password_hash, create_access_token
from app.models.user import User

# client and test_db fixtures are provided by conftest.py


def test_create_user(
    client, test_db: Session
):  # Keeping test_db as it's common practice
    user_data = {  # Assuming UserCreate model_dump() produces a dict like this
        "username": "new_test_user",
        "password": "new_test_password",
    }

    response = client.post("/users/", json=user_data)  # Using the simple dict for now

    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json["username"] == "new_test_user"
    assert "id" in response_json  # It's good practice to assert the ID is returned
    # Optionally, you could use test_db here to query and verify the user exists
    # user_in_db = test_db.query(User).filter(User.username == "new_test_user").first()
    # assert user_in_db is not None
    # assert user_in_db.id == response_json["id"]


def test_create_user_conflict(client, test_db: Session):
    # First create a user to get into conflict
    conflict_username = "conflict_user_test"
    user_data_initial = UserCreate(
        username=conflict_username, password="password123"
    ).model_dump()  # UPDATED
    initial_response = client.post("/users/", json=user_data_initial)
    assert (
        initial_response.status_code == status.HTTP_201_CREATED
    )  # Ensure first user is created

    # Try creating the same user which has already been created
    user_data_conflict = UserCreate(
        username=conflict_username, password="password456"
    ).model_dump()  # UPDATED
    conflict_response = client.post("/users/", json=user_data_conflict)

    assert (
        conflict_response.status_code == status.HTTP_400_BAD_REQUEST
    )  # Assuming your API returns 400 for username conflict


def test_get_me(client, test_db: Session):
    my_username = "user_get_me"
    hashed_password = get_password_hash("password_get_me")
    test_user = User(username=my_username, hashed_password=hashed_password)
    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)

    token = create_access_token(data={"user_id": str(test_user.id)})
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == my_username
    assert response.json()["id"] == test_user.id


def test_get_me_unauthorised(client):
    response = client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_user(client, test_db: Session):
    target_username = "target_user_get"
    hashed_password = get_password_hash("password_target")
    target_user = User(username=target_username, hashed_password=hashed_password)
    test_db.add(target_user)
    test_db.commit()
    test_db.refresh(target_user)

    auth_user_username = "auth_user_for_get_target"
    auth_user_hashed_pw = get_password_hash("auth_user_pw")
    auth_user = User(username=auth_user_username, hashed_password=auth_user_hashed_pw)
    test_db.add(auth_user)
    test_db.commit()
    test_db.refresh(auth_user)
    token = create_access_token(data={"user_id": str(auth_user.id)})

    response = client.get(
        f"/users/{target_user.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == target_username
    assert response.json()["id"] == target_user.id


def test_get_user_not_found(client, test_db: Session):
    # Authenticate as some user to make the request
    auth_user_username = "auth_user_for_not_found"
    auth_user_hashed_pw = get_password_hash("auth_user_pw_nf")
    auth_user = User(username=auth_user_username, hashed_password=auth_user_hashed_pw)
    test_db.add(auth_user)
    test_db.commit()
    test_db.refresh(auth_user)
    token = create_access_token(data={"user_id": str(auth_user.id)})

    non_existent_user_id = 999999  # An ID that is unlikely to exist
    response = client.get(
        f"/users/{non_existent_user_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
