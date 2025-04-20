# app/schemas/user.py

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username of the user",
    )
    email: EmailStr
    
class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters long and include at least one uppercase, one lowercase, one digit, and one special character.",
    )
    
class UserUpdate(BaseModel):
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="New username of the user",
    )
    email: Optional[EmailStr] = Field(
        None,
        description="New email of the user",
    )
    is_verified: Optional[bool] = Field(
        None,
        description="Mark the user as verified or not (admin use)",
    )
    
class UserOut(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_verified: bool
    verification_token: Optional[str]
    full_name: Optional[str]
    phone_number: Optional[str]
    
    class Config:
        orm_mode = True
        
        
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    sub: Optional[str] = None