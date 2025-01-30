from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas.base import TimestampedSchema

class UserBase(BaseModel):
    email: EmailStr
    name: str
    is_active: bool = True
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase, TimestampedSchema):
    pass

class UserInDB(UserResponse):
    password: str