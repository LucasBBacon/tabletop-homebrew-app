from typing import Optional
from uuid import uuid4

from app.models.user import User
from app.models.user import User as UserORM

# fake_users_db = {}

# def get_user_by_username(username: str) -> Optional[UserInDB]:
#     return fake_users_db.get(username)


# def get_user_by_email(email: str) -> Optional[UserInDB]:
#     for user in fake_users_db.values():
#         if user.email == email:
#             return user
#     return None


# def get_user_by_verification_token(token: str) -> Optional[UserInDB]:
#     for user in fake_users_db.values():
#         if user.verification_token == token:
#             return user
#     return None


# def save_user(user: UserInDB):
#     fake_users_db[user.username] = user

from sqlalchemy.orm import Session

def get_user_by_username(db: Session, username: str) -> UserORM | None:
    return db.query(UserORM).filter(UserORM.username == username).first()

def get_user_by_email(db: Session, email: str) -> UserORM | None:
    return db.query(UserORM).filter(UserORM.email == email).first()

def get_user_by_verification_token(db: Session, token: str) -> UserORM | None:
    return db.query(UserORM).filter(UserORM.verification_token == token).first()

def create_user(db: Session, username: str, email: str, hashed_password: str) -> UserORM:
    user = UserORM(
        username=username,
        email=email,
        hashed_password=hashed_password,
        verification_token=str(uuid4())
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user: UserORM, **fields) -> UserORM:
    for key, value in fields.items():
        setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user