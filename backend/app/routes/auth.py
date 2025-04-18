# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm

# from app.core.security import (
#     create_access_token,
#     hash_password,
#     verify_password
#     )
# from app.database.crud import (
#     get_user_by_email, 
#     get_user_by_username, 
#     get_user_by_verification_token, 
#     save_user
#     )
# from app.models.user import Token, UserCreate, UserInDB


# router = APIRouter()

# @router.post("/register", status_code=status.HTTP_201_CREATED)
# async def register(user_data: UserCreate):
#     """
#     Register a new user.
#     """
#     # validate that use does not already exist
#     exting_user = get_user_by_username(user_data.username)
#     if exting_user:
#         raise HTTPException(
#             status_code=400,
#             detail="Username already registered"
#             )
    
#     existing_email = get_user_by_email(user_data.email)
#     if existing_email:
#         raise HTTPException(
#             status_code=400,
#             detail="Email already registered"
#             )

#     # Hash the password and create the user
#     hashed = hash_password(user_data.password)
#     new_user = UserInDB(
#         username=user_data.username,
#         email=user_data.email,
#         hashed_password=hashed
#     )
#     save_user(new_user)
#     return {"msg": "User registered successfully"}


# @router.post("/login", response_model=Token)
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     """
#     Login a user and return an access token.
#     """
#     user = get_user_by_username(form_data.username)
#     if not user or not verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = create_access_token(data={"sub": user.username})
#     return {"access_token": access_token, "token_type": "bearer"}


# @router.post("/verify-email")
# async def verify_email(token: str):
#     user = get_user_by_verification_token(token)
#     if not user:
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid or expired verification token"
#         )
#     user.is_verified = True
#     save_user(user)
#     return {
#         "success": True,
#         "message": "Email verified successfully",
#     }

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.user import UserCreate
from app.schemas.auth import Token, TokenData
from app.core.security import create_access_token, hash_password, verify_password
from app.database.crud import (
    create_user, 
    get_user_by_email, 
    get_user_by_username, 
    get_user_by_verification_token, 
    update_user
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
            "Username already registered"
            )
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, 
            "Email already registered"
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
    
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login a user and return an access token.
    """
    # Validate user credentials
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Issue JWT token
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token, 
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
            detail="Invalid or expired verification token"
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