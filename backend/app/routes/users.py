from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.database.crud import get_user_by_username, save_user
from app.models.user import User, UserInDB, UserUpdate


router = APIRouter()

@router.get("/profile", response_model=User)
async def read_profile(current_user: UserInDB = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=User)
async def update_profile(
    updated_data: UserUpdate, 
    current_user: UserInDB = Depends(get_current_user)
    ):
    # Update Logic: for example, update username/email. Handle password separately
    if updated_data.username:
        if updated_data.username != current_user.username and get_user_by_username(updated_data.username):
            raise HTTPException(
                status_code=400,
                detail="Username already registered"
            )
        else:
            current_user.username = updated_data.username

    if updated_data.email:
        current_user.email = updated_data.email
        
    if updated_data.is_verified:
        current_user.is_verified = updated_data.is_verified

    # Save the updated user back to the fake database
    save_user(current_user)
    return current_user
