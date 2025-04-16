from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.exceptions.handlers import (
    EmailVerificationError, 
    email_verification_exception_handler, 
    http_exception_handler, 
    validation_exception_handler
    )
from app.routes import auth, users

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)


app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(EmailVerificationError, email_verification_exception_handler)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])

@app.get("/api/ping/", summary="Ping the API")
async def ping():
    """
    Ping the API to check if it's running.
    """
    return {"message": "Pong!"}