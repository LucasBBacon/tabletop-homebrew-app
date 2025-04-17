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
    )
    email: Optional[EmailStr] = None
    is_verified: Optional[bool] = None
    
class UserOut(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_verified: bool
    full_name: Optional[str]
    phone_number: Optional[str]
    
    class Config:
        orm_mode = True
        
        
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    sub: Optional[str] = None