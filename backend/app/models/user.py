from datetime import datetime
import re
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, EmailStr, Field, field_validator


class Token(BaseModel):
    """
    Token model for OAuth2 authentication.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Token data model.
    """
    sub: Optional[str] = None


class User(BaseModel):
    """
    User model for the API.
    """
    id: str = Field(default_factory = lambda: str(uuid4()))
    username: str = Field(
        min_length=3,
        max_length=50
    )
    email: EmailStr


class UserInDB(User):
    """
    User model for the database.
    """
    hashed_password: str
    created_at : Optional[datetime] = Field(default_factory=datetime.now)
    updated_at : Optional[datetime] = Field(default_factory=datetime.now)
    is_active : Optional[bool] = True
    is_verified : Optional[bool] = False
    verification_token : Optional[str] = None
    full_name : Optional[str] = None
    phone_number : Optional[str] = None


class UserCreate(BaseModel):
    """
    User registration model. 
    Password must be at least 8 characters long and include at least one uppercase, one lowercase, one digit, and one special character.
    """
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50, 
        description="Username must be between 3 and 50 characters long and cannot contain spaces."
        )
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters long and include at least one uppercase, one lowercase, one digit, and one special character."
        )

    @field_validator('username')
    def validate_username(cls, username: str) -> str:
        if " " in username:
            raise ValueError("Username cannot contain spaces.")
        return username
    
    @field_validator('password')
    def validate_password(cls, password: str) -> str:
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).+$'
        if not re.match(pattern, password):
            raise ValueError(
                "Password must include at least one uppercase letter, one lowercase letter, one digit, and one special character."
            )
        return password
    


class ExtendedUserCreate(UserCreate):
    full_name : str = Field(
        None, 
        max_length=100
        )
    phone_number : str = Field(
        None, 
        pattern=r'^\+?[1-9]\d{1,14}$', 
        description="Phone number must be in E.164 format."
        )


class UserUpdate(BaseModel):
    """
    User update model.
    """
    username: Optional[str] = Field(
        None, 
        min_length=3, 
        max_length=50
    )
    email: Optional[EmailStr] = None
    is_verified: Optional[bool] = None