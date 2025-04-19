from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.exceptions.handlers import (
    EmailVerificationError, 
    email_verification_exception_handler, 
    http_exception_handler, 
    validation_exception_handler
    )
from app.routes import auth, users
from app.database.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Create the database tables on startup and drop them on shutdown.
    """
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the database tables
    Base.metadata.drop_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(EmailVerificationError, email_verification_exception_handler)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])


@app.get("/api/ping", summary="Ping the API")
async def ping():
    """
    Ping the API to check if it's running.
    """
    return {"message": "Pong!"}