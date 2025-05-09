# app/core/security.py

from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.crud import get_user_by_username
from app.core.redis import is_token_blacklisted
from app.schemas.auth import TokenData
from app.models.user import User as UserORM
from app.database.database import get_db



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None,
    token_type: str = "access"
):
    """
    Create an access token with an expiration time.
    """
    to_encode = data.copy()
    now = datetime.now()
    expire = now + (expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "iat": now.timestamp(), 
        "exp": expire.timestamp(),
        "jti": str(uuid4()),
        "type": token_type
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserORM:
    """
    Get the current user from the token.
    """
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            print("Username not found in token payload")
            raise credentials_exception
        token_data = TokenData(sub=username)
    except JWTError as e:
        print(f"JWT decoding error: {e}")
        raise credentials_exception
    
    user = get_user_by_username(db, username=token_data.sub)
    if user is None:
        print(f"User not found: {token_data.sub}")
        raise credentials_exception
    return user