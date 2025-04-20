# app/routes/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.messages import EMAIL_ALREADY_REGISTERED, USERNAME_ALREADY_REGISTERED
from app.core.security import get_current_user
from app.database.crud import get_user_by_username, update_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate


router = APIRouter()

@router.get("/profile", response_model=UserOut)
def read_profile(current_user: User = Depends(get_current_user)):
    # Current user is already injected by the dependency
    return current_user

@router.put("/profile", response_model=UserOut)
def update_profile(
    updated_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # If changing username, check if the new username is already taken
    if updated_data.username and updated_data.username != current_user.username:
        if get_user_by_username(db, updated_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=USERNAME_ALREADY_REGISTERED
            )
    # If changing email, check if the new email is already taken
    if updated_data.email and updated_data.email != current_user.email:
        if get_user_by_username(db, updated_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=EMAIL_ALREADY_REGISTERED
            )
    # Perform the update and persist
    user = update_user(
        db,
        current_user,
        **{k: v for k, v in updated_data.model_dump(exclude_none=True).items()}
    )
    return user