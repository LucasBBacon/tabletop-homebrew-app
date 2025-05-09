# app/database/crud.py

from uuid import uuid4

from app.models.user import User as UserORM
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

blacklist_tokens = set()

def blacklist_token(token: str) -> None:
    blacklist_tokens.add(token)

def is_token_blacklisted(token: str) -> bool:
    return token in blacklist_tokens