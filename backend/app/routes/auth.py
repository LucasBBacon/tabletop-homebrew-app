# app/routes/auth.py

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt

from app.core.config import settings
from app.database.database import get_db
from app.schemas.user import UserCreate
from app.schemas.auth import Token, TokenPair, TokenRefreshRequest
from app.core.security import (
    create_access_token, 
    hash_password, 
    verify_password, 
    oauth2_scheme
)
from app.database.crud import (
    create_user, 
    get_user_by_email, 
    get_user_by_username, 
    get_user_by_verification_token, 
    update_user
)
from app.core.redis import blacklist_token, is_token_blacklisted
from app.core.messages import (
    EMAIL_ALREADY_REGISTERED, 
    INVALID_CREDENTIALS,
    INVALID_TOKEN,
    REFRESH_TOKEN_REVOKED, 
    USERNAME_ALREADY_REGISTERED
)


router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    # Validate that the user does not already exist
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, 
            USERNAME_ALREADY_REGISTERED
            )
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, 
            EMAIL_ALREADY_REGISTERED
            )
    # Hash the password and create the user
    hashed = hash_password(user_data.password)
    user = create_user(
        db, 
        username=user_data.username,
        email=user_data.email, 
        hashed_password=hashed
        )
    return {
        "msg": "User registered successfully",
        "id": str(user.id),
    }
    
@router.post("/login", response_model=TokenPair)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login a user and return an access token.
    """
    # Validate user credentials
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS,
        )
    # Issue JWT token
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(days=7),
        token_type="refresh"
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
    
@router.post("/refresh-token", response_model=Token)
def refresh_token(token_data: TokenRefreshRequest):
    """
    Refresh the access token using a valid refresh token.
    """
    if is_token_blacklisted(token_data.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=REFRESH_TOKEN_REVOKED,
        )
    try:
        payload = jwt.decode(
            token_data.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_TOKEN,
            )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_TOKEN,
        )
    
    new_access_token = create_access_token(
        data={"sub": username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.post("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify user email using a token.
    """
    # Validate the token and get the user
    user = get_user_by_verification_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_TOKEN,
        )
    # Update user verification status
    user = update_user(
        db, 
        user, 
        is_verified=True
    )
    return {
        "success": True,
        "message": "Email verified successfully",
    }
    
@router.post("/logout")
def logout(
    current_token: str = Depends(oauth2_scheme),
    refresh_token_payload: TokenRefreshRequest = None
):
    """
    Logout a user by blacklisting the access token and refresh token.
    """
    # Blacklist the access token
    blacklist_token(current_token)
    # If a refresh token is provided, blacklist it as well
    if refresh_token_payload and refresh_token_payload.refresh_token:
        blacklist_token(refresh_token_payload.refresh_token)
    return {
        "success": True,
        "message": "Logged out successfully",
    }