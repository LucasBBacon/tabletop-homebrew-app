from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

app = FastAPI()

SECRET_KEY = "waucydelgaucy"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# region Models

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None

class User(BaseModel):
    id: str
    username: str
    email: EmailStr

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

# endregion Models


# region Token Creation and Verification

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    now = datetime.astimezone(datetime.now())
    expire = now + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update({"iat": now, "exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

# endregion Token Creation and Verification


# region fake database

fake_users_db = {}

def get_user_by_username(username: str) -> Optional[UserInDB]:
    return fake_users_db.get(username)

def save_user(user: UserInDB):
    fake_users_db[user.username] = user

# endregion fake database


# region OAuth2 Scheme for protected routes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception
        
        token_data = TokenData(sub=username)

    except JWTError:
        raise credentials_exception
    
    user = get_user_by_username(username=token_data.sub)
    if user is None:
        raise credentials_exception
    
    return user
    
# endregion OAuth2 Scheme for protected routes


@app.get("/api/ping")
async def ping():
    return {"message": "pong"}


@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    # validate that use does not already exist
    if get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
            )
    
    # Hash the password and create the user
    hashed = hash_password(user_data.password)
    # In a real app, generate UUID here. For proptyping, a fixed string is used
    new_user = UserInDB(
        id="generate-uuid-here",
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed
    )
    save_user(new_user)

    return {"msg": "User registered successfully"}


@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_username(form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/profile", response_model=User)
async def read_profile(current_user: UserInDB = Depends(get_current_user)):
    return current_user


@app.put("/users/profile", response_model=User)
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

    # Save the updated user back to the fake database
    save_user(current_user)

    return current_user