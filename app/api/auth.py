from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

# Assuming these are correctly defined in your project structure
from app.api.dependencies import get_db
from app.api.schemas import Token, UserCreate  # Ensure these Pydantic models are defined
from app.core.config import settings
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token
)
# Assuming these service functions are defined, possibly in app/services/user_service.py
# and are compatible with async/await if your path operations are async.
# If they are synchronous, you might not need 'await' or ensure FastAPI handles it.
from app.services.user_service import (
    get_user_by_username,
    create_user
)

# This router will be included with a prefix, e.g., "/auth" in app/api/routes.py
router = APIRouter()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_up(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Handles new user registration.
    Checks if the username already exists before creating a new user.
    """
    # Check if user already exists
    existing_user = await get_user_by_username(db, username=user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered. Please choose a different username."
        )

    # Hash the password before storing
    hashed_password = get_password_hash(user_data.password)

    # Create the new user
    # Ensure your create_user service function handles the actual database insertion
    # and matches the parameters (e.g., username, hashed_password, potentially email from UserCreate)
    new_user = await create_user(db, username=user_data.username, hashed_password=hashed_password,
                                 email=user_data.email if hasattr(user_data, 'email') else None)

    # You might want to return the created user (excluding password) or just a success message
    return {"message": "User created successfully. Please login."}


@router.post("/login", response_model=Token)
async def login_for_access_token(  # Renamed function for clarity, was 'login'
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    """
    Handles user login and returns an access token.
    This endpoint will be accessible at /auth/login if auth.router is included with prefix "/auth".
    Your tests were previously trying to call "/token".
    """
    # Authenticate the user
    user = await get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},  # Standard practice for 401 with Bearer tokens
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": str(user.id)},  # 'sub' is standard, ensure user.id is available
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

# If you want a "/token" endpoint directly, you could define it here:
# @router.post("/token", response_model=Token)
# async def get_token_alias( ... ):
#     # This would be accessible at /auth/token
#     # Or, you could change "/login" above to "/token"
#     # Or, include this auth.router without the "/auth" prefix in app/api/routes.py
#     # if you want a root "/token" endpoint.
#     return await login_for_access_token(form_data, db)

