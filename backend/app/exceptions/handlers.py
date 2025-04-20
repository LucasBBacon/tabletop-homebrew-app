# app/exceptions/handlers.py

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

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.messages import INTERNAL_SERVER_ERROR



class EmailVerificationError(Exception):
    """
    Custom exception for email verification errors.
    """
    def __init__(self, message: str):
        self.message = message
        

async def validation_exception_handler(request: Request, exc: RequestValidationError):
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
            "message": INTERNAL_SERVER_ERROR,
            "detail": str(exc),
        },
    )