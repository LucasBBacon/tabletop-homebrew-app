from datetime import timedelta
from fastapi.testclient import TestClient
from backend.main import app, create_access_token


client = TestClient(app)

# region Helper login function

def register_user(username: str, email: str, password: str):
    return client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )

def login_user(username: str, password: str):
    return client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password
        }
    )

# endregion Helper login function



# region Duplicate registration test

def test_duplicate_registration():
    """
    Test that attempting to register a user with an existing username fails.
    """

    # First registration should succeed
    response1 = register_user(
        "dupuser",
        "dupuser@example.com",
        "Testpassword123!"
    )
    assert response1.status_code == 201, "The first registration should succeed."

    # Second registration with same username/email should fail
    response2 = register_user(
        "dupuser",
        "dupuser@example.com",
        "Testpassword123!"
    )
    # Expect a 400 Bad Request error, based on route logic checking for existing users
    assert response2.status_code == 400, "Re-gistration with existing username should fail."
    # Optionally verify error message contains reference to duplication
    assert "already" in response2.json().get("message").lower()\
        , "Error message should indicate duplication."

# endregion Duplicate registration test



# region Invalid token test

def test_invalid_token():
    """
    Test that accessing a protected endpoint with an invalid token fails.
    """

    # Create an invalid token header
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/users/profile", headers=headers)
    # The absence of a valid token should return a 401 Unauthorized error
    assert response.status_code == 401,\
        "Invalid token should return 401 Unauthorized."

# endregion Invalid token test



# region Expired token test

def test_expired_token():
    """
    Test that accessing a protected endpoint with an expired token fails.
    """

    # Create an expired token by providing a negative timedelta
    expired_token = create_access_token(
        data={"sub": "testuser"},
        expires_delta=timedelta(days=-1)  # Token expired yesterday
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/users/profile", headers=headers)
    # Expired tokens should return a 401 Unauthorized error
    assert response.status_code == 401,\
        "Expired token should return 401 Unauthorized."

# endregion Expired token test



# region Malformed input data registration test

def test_malformed_input_registration():
    """
    Test that attempting to register a user with malformed input data fails.
    """

    # Here the email format is invalid, and the password is too short
    response = client.post(
        "/auth/register",
        json={
            "username": "malformeduser",
            "email": "invalid-email-format",
            "password": "123"
        }
    )

    # Expect a 422 Unprocessable Entity error, based on FastAPI's validation
    assert response.status_code == 422,\
        "Malformed input should return 422 Unprocessable Entity."

# endregion Malformed input data registration test