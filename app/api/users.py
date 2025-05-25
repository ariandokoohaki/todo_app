# app/api/users.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core import security  # For get_current_active_user, get_password_hash
from app.services import user_service
from app.api import schemas  # For UserCreate, UserRead, UserUpdate etc.
from app.models.user import User as UserModel  # For type hinting current_user

router = APIRouter()


@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def create_new_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create new user.
    This is where the F841 'new_user' (or similar variable) fix is applied
    by ensuring the created user object is returned.
    """
    db_user = await user_service.get_user_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    hashed_password = security.get_password_hash(user_in.password)

    # The user_service.create_user function should return the created user model
    created_user_model = await user_service.create_user(
        db=db,
        username=user_in.username,
        hashed_password=hashed_password,
        email=user_in.email,  # Assuming email is part of UserCreate
    )

    # Return the Pydantic model created from the ORM model
    # Pydantic v2: schemas.UserRead.model_validate(created_user_model)
    # Pydantic v1: schemas.UserRead.from_orm(created_user_model)
    # FastAPI handles this conversion automatically if response_model is set
    # and the Pydantic model has orm_mode=True (v1) or from_attributes=True (v2)
    return created_user_model


@router.get("/me", response_model=schemas.UserRead)
async def read_users_me(
    current_user: UserModel = Depends(security.get_current_active_user),
):
    """
    Get current user.
    """
    # current_user is already the ORM model instance from the dependency
    return current_user


@router.get("/{user_id}", response_model=schemas.UserRead)
async def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    # Optional: Add current_user dependency if only specific users can view others
    # current_user: UserModel = Depends(security.get_current_active_user)
):
    """
    Get a specific user by id.
    """
    db_user = await user_service.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return db_user


@router.get("/", response_model=List[schemas.UserRead])
async def read_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    Retrieve users with pagination.
    Consider protecting this endpoint (e.g., admin only).
    """
    users = await user_service.get_users(db, skip=skip, limit=limit)
    return users


@router.put("/{user_id}", response_model=schemas.UserRead)
async def update_existing_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(security.get_current_active_user),
):
    """
    Update a user. Users can update their own info, or admins can update any.
    """
    db_user = await user_service.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Authorization: Ensure user is updating themselves or is an admin
    # This is a simplified check; you might have more complex role-based access
    if (
        db_user.id != current_user.id and not current_user.is_superuser
    ):  # Assuming an is_superuser field
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    updated_user_model = await user_service.update_user(
        db=db, user_model=db_user, user_update_schema=user_in
    )
    return updated_user_model


# You might also want a DELETE endpoint:
# @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_existing_user(
#     user_id: int,
#     db: Session = Depends(get_db),
#     current_user: UserModel = Depends(security.get_current_active_user)
# ):
#     # Similar logic for fetching user and authorization
#     # Then call a user_service.delete_user(db=db, user_id=user_id)
#     pass
