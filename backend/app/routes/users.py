# from fastapi import APIRouter, Depends, HTTPException

# from app.core.security import get_current_user
# from app.database.crud import get_user_by_username, save_user
# from app.models.user import User, UserInDB, UserUpdate


# router = APIRouter()

# @router.get("/profile", response_model=User)
# async def read_profile(current_user: UserInDB = Depends(get_current_user)):
#     return current_user


# @router.put("/profile", response_model=User)
# async def update_profile(
#     updated_data: UserUpdate, 
#     current_user: UserInDB = Depends(get_current_user)
#     ):
#     # Update Logic: for example, update username/email. Handle password separately
#     if updated_data.username:
#         if updated_data.username != current_user.username and get_user_by_username(updated_data.username):
#             raise HTTPException(
#                 status_code=400,
#                 detail="Username already registered"
#             )
#         else:
#             current_user.username = updated_data.username

#     if updated_data.email:
#         current_user.email = updated_data.email
        
#     if updated_data.is_verified:
#         current_user.is_verified = updated_data.is_verified

#     # Save the updated user back to the fake database
#     save_user(current_user)
#     return current_user

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.crud import get_user_by_username, update_user
from app.database.database import get_db
from app.schemas.user import UserOut, UserUpdate
from app.models.user import User


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
                detail="Username already registered"
            )
    # If changing email, check if the new email is already taken
    if updated_data.email and updated_data.email != current_user.email:
        if get_user_by_username(db, updated_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    # Perform the update and persist
    user = update_user(
        db,
        current_user,
        **{k: v for k, v in updated_data.model_dump(exclude_none=True).items()}
    )
    return user