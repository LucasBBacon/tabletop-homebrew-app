from typing import Optional

from app.models.user import UserInDB

fake_users_db = {}

def get_user_by_username(username: str) -> Optional[UserInDB]:
    return fake_users_db.get(username)


def get_user_by_email(email: str) -> Optional[UserInDB]:
    for user in fake_users_db.values():
        if user.email == email:
            return user
    return None


def get_user_by_verification_token(token: str) -> Optional[UserInDB]:
    for user in fake_users_db.values():
        if user.verification_token == token:
            return user
    return None


def save_user(user: UserInDB):
    fake_users_db[user.username] = user