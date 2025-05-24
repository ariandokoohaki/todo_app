from pydantic import BaseModel
from typing import Optional

#
# Auth schemas
#

class Token(BaseModel):
    access_token: str
    token_type: str

#
# User schemas
#

class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

#
# Todo schemas
#

class TodoCreate(BaseModel):
    title: str
    description: str

class TodoRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    owner_id: int

    class Config:
        from_attributes = True

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
