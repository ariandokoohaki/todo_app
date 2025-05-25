# app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core import security  # For create_access_token, verify_password
from app.core.config import settings  # For ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.database import get_db
from app.services import user_service  # For get_user_by_username
from app.api import schemas  # For Token schema

router = APIRouter()


@router.post("/login/token", response_model=schemas.Token)
async def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await user_service.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username, "user_id": user.id},  # Add user_id to token
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
