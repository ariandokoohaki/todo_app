from fastapi import status
from sqlalchemy.orm import Session # Added for type hinting if not already there

# Assuming these are correctly defined in your project structure
from app.api.schemas import TodoCreate
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
# from app.models.todo import Todo # Not directly used in this file for instantiation

# client and test_db fixtures are provided by conftest.py

def test_create_todo(client, test_db: Session):
    hashed_password = get_password_hash("test_password_todo_create") # Unique username for test isolation
    test_user = User(username="user_for_todo_create", hashed_password=hashed_password)
    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user) # Get the user ID

    token = create_access_token(data={"user_id": str(test_user.id)}) # Ensure user_id is string if JWT expects str
    todo_data = TodoCreate(title="test_todo_creation", description="test_description_creation").model_dump() # UPDATED
    response = client.post("/todos/", json=todo_data, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json["title"] == "test_todo_creation"
    assert response_json["description"] == "test_description_creation"
    assert response_json["owner_id"] == test_user.id # Verify owner_id

def test_create_todo_unauthorised(client, test_db: Session): # test_db might not be needed if no setup
    todo_data = TodoCreate(title="test_todo_unauth", description="test_description_unauth").model_dump() # UPDATED
    response = client.post("/todos/", json=todo_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_todos(client, test_db: Session):
    hashed_password = get_password_hash("test_password_get_todos")
    test_user = User(username="user_for_get_todos", hashed_password=hashed_password)
    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)

    token = create_access_token(data={"user_id": str(test_user.id)})

    # Create a todo for the user
    todo_to_create_data = TodoCreate(title="test_todo_for_get", description="test_desc_for_get").model_dump() # UPDATED
    create_response = client.post("/todos/", json=todo_to_create_data, headers={"Authorization": f"Bearer {token}"})
    assert create_response.status_code == status.HTTP_201_CREATED # Ensure creation was successful

    response = client.get("/todos/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, list) # Should be a list
    assert len(response_json) > 0
    # Find the created todo in the list (order might not be guaranteed)
    found_todo = next((item for item in response_json if item["title"] == "test_todo_for_get"), None)
    assert found_todo is not None
    assert found_todo["description"] == "test_desc_for_get"
    assert found_todo["owner_id"] == test_user.id

def test_get_todos_unauthorised(client):
    response = client.get("/todos/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
