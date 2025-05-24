from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List  # For potential future list responses

from app.api.dependencies import get_db, get_current_user
from app.api.schemas import UserRead, UserUpdate, UserCreate
from app.models.user import User  # Your SQLAlchemy User model
from app.core.security import get_password_hash

# --- Import user-related services from your user_service.py ---
from app.services.user_service import (
    create_user as create_user_service,  # Alias if needed, or use directly
    get_user_by_username,  # For checking existence if needed during creation
    get_user_by_id
)

# --- End of service imports ---

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED, summary="Create New User")
async def create_new_user(
        user_data: UserCreate,
        db: Session = Depends(get_db)
):
    # Optional: Check if user already exists (can also be handled in service)
    existing_user = await get_user_by_username(db, username=user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered."
        )
    # Add email check if your UserCreate schema and User model have email
    # if hasattr(user_data, 'email') and user_data.email:
    #     from app.services.user_service import get_user_by_email # Assuming you'd add this service
    #     existing_email_user = await get_user_by_email(db, email=user_data.email)
    #     if existing_email_user:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    hashed_password = get_password_hash(user_data.password)

    # Use your create_user service
    new_user = await create_user_service(
        db,
        username=user_data.username,
        hashed_password=hashed_password
        # Pass email if your service and model handle it:
        # email=user_data.email if hasattr(user_data, 'email') else None
    )
    return new_user


@router.get("/me", response_model=UserRead, summary="Get Current User Profile")
async def get_me(
        current_user: User = Depends(get_current_user)
):
    return current_user


@router.patch("/me", response_model=UserRead, summary="Update Current User Profile")
async def update_me(
        user_data: UserUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    update_data_dict = user_data.model_dump(exclude_unset=True)  # Pydantic v2

    if "username" in update_data_dict:
        # Optional: Check if new username is already taken by another user
        # if update_data_dict["username"] != current_user.username:
        #     existing_user = await get_user_by_username(db, username=update_data_dict["username"])
        #     if existing_user:
        #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New username is already taken.")
        current_user.username = update_data_dict["username"]

    if "password" in update_data_dict and update_data_dict["password"] is not None:
        current_user.hashed_password = get_password_hash(update_data_dict["password"])

    # Handle email update if your User model and UserUpdate schema support it
    # if "email" in update_data_dict and hasattr(current_user, 'email'):
    #     # Optional: Check if new email is already taken
    #     current_user.email = update_data_dict["email"]

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/{user_id}", response_model=UserRead, summary="Get User by ID")
async def read_user_by_id(
        user_id: int,
        db: Session = Depends(get_db),
        # current_user: User = Depends(get_current_user) # Uncomment if only authenticated users can fetch other users
):
    # Use your get_user_by_id service
    db_user = await get_user_by_id(db, user_id=user_id)

    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user
