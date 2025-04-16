from datetime import datetime, timedelta
import re
from typing import Optional
from uuid import uuid4
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, Field, field_validator
from passlib.context import CryptContext

app = FastAPI()

SECRET_KEY = "waucydelgaucy"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# region Models

class Token(BaseModel):
    """
    Token model for OAuth2 authentication.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Token data model.
    """
    sub: Optional[str] = None


class User(BaseModel):
    """
    User model for the API.
    """
    id: str = Field(default_factory = lambda: str(uuid4()))
    username: str = Field(
        min_length=3,
        max_length=50
    )
    email: EmailStr


class UserInDB(User):
    """
    User model for the database.
    """
    hashed_password: str
    created_at : Optional[datetime] = Field(default_factory=datetime.now)
    updated_at : Optional[datetime] = Field(default_factory=datetime.now)
    is_active : Optional[bool] = True
    is_verified : Optional[bool] = False
    verification_token : Optional[str] = None
    full_name : Optional[str] = None
    phone_number : Optional[str] = None


class UserCreate(BaseModel):
    """
    User registration model. 
    Password must be at least 8 characters long and include at least one uppercase, one lowercase, one digit, and one special character.
    """
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50, 
        description="Username must be between 3 and 50 characters long and cannot contain spaces."
        )
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters long and include at least one uppercase, one lowercase, one digit, and one special character."
        )

    @field_validator('username')
    def validate_username(cls, username: str) -> str:
        if " " in username:
            raise ValueError("Username cannot contain spaces.")
        return username
    
    @field_validator('password')
    def validate_password(cls, password: str) -> str:
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).+$'
        if not re.match(pattern, password):
            raise ValueError(
                "Password must include at least one uppercase letter, one lowercase letter, one digit, and one special character."
            )
        return password
    


class ExtendedUserCreate(UserCreate):
    full_name : str = Field(
        None, 
        max_length=100
        )
    phone_number : str = Field(
        None, 
        pattern=r'^\+?[1-9]\d{1,14}$', 
        description="Phone number must be in E.164 format."
        )


class UserUpdate(BaseModel):
    """
    User update model.
    """
    username: Optional[str] = Field(
        None, 
        min_length=3, 
        max_length=50
    )
    email: Optional[EmailStr] = None
    is_verified: Optional[bool] = None

# endregion Models


# region Token Creation and Verification

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create an access token with an expiration time.
    """
    to_encode = data.copy()
    now = datetime.astimezone(datetime.now())
    expire = now + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"iat": now, "exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# endregion Token Creation and Verification


# region Fake database

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

# endregion Fake database


# region OAuth2 Scheme for protected routes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """
    Get the current user from the token.
    """
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


# region Routes

@app.get("/api/ping")
async def ping():
    return {"message": "pong"}


@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user.
    """
    # validate that use does not already exist
    exting_user = get_user_by_username(user_data.username)
    if exting_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
            )
    
    existing_email = get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
            )

    # Hash the password and create the user
    print("TEST")
    hashed = hash_password(user_data.password)
    # In a real app, generate UUID here. For proptyping, a fixed string is used
    new_user = UserInDB(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed
    )
    save_user(new_user)
    return {"msg": "User registered successfully"}


@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login a user and return an access token.
    """
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
        
    if updated_data.is_verified:
        current_user.is_verified = updated_data.is_verified

    # Save the updated user back to the fake database
    save_user(current_user)
    return current_user


@app.post("/auth/verify-email")
async def verify_email(token: str):
    user = get_user_by_verification_token(token)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification token"
        )
    user.is_verified = True
    save_user(user)
    return {
        "success": True,
        "message": "Email verified successfully",
    }


# endregion Routes



# region Exception Handlers

"""
Custom exception handlers for the FastAPI application.
Standard response schema is defined for consistency.
{
    "success": bool, True if the request was successful, False otherwise.
    "error_code": str, A short string or code that identifies the error type.
    "message": str, A human-readable message describing the error.
    "detail": Optional[dict] An optional dictionary containing additional details about the error.
}
"""

class EmailVerificationError(Exception):
    """
    Custom exception for email verification errors.
    """
    def __init__(self, message: str):
        self.message = message
        

@app.exception_handler(RequestValidationError)
async def validation_Exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom exception handler for validation errors.
    """
    cleaned_errors = []

    # Iterate through the errors and clean them
    errors = exc.errors()
    for error in errors:
        msg = error.get("msg")
        if not isinstance(msg, str):
            msg = str(msg)
        error_copy = error.copy()
        error_copy["msg"] = msg

        # Process context if present
        if "ctx" in error_copy:
            ctx = error_copy["ctx"]
            if isinstance(ctx, dict):
                new_ctx = {
                    k: (
                        str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
                        ) for k, v in ctx.items()
                }
                error_copy["ctx"] = new_ctx
                
        cleaned_errors.append(error_copy)
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": "Input validation failed.",
            "detail": cleaned_errors,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom exception handler for HTTP exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": "HTTP_ERROR",
            "message": exc.detail,
        }
    )


@app.exception_handler(EmailVerificationError)
async def email_verification_exception_handler(request: Request, exc: EmailVerificationError):
    """
    Custom exception handler for email verification errors.
    """
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error_code": "EMAIL_VERIFICATION_ERROR",
            "message": exc.message,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Custom exception handler for generic exceptions.
    """
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
            "detail": str(exc),
        },
    )

# endregion Exception Handlers