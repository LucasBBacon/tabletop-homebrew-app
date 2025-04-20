# app/core/messages.py

# region Authentication Errors

INVALID_CREDENTIALS = "Incorrect username or password."
INVALID_TOKEN = "Invalid or expired token."
TOKEN_REVOKED = "Token has been revoked."
REFRESH_TOKEN_REVOKED = "Refresh token has been revoked."

# endregion Authentication Errors


# region Registration Errors

USERNAME_ALREADY_REGISTERED = "Username already registered."
EMAIL_ALREADY_REGISTERED = "Email already registered."

# endregion Registration Errors


# region Verification Errors

INVALID_VERIFICATION_TOKEN = "Invalid or expired verification token."

#endregion Verification Errors


# region Generic Errors

COULD_NOT_VALIDATE_CREDENTIALS = "Could not validate credentials."
INTERNAL_SERVER_ERROR = "An unexpected internal server error occurred."

# endregion Generic Errors