from fastapi.testclient import TestClient
import pytest
from backend.main import app


client = TestClient(app)


# region Registration Validation Tests

def test_registration_invalid_email():
    """
    Test registration with an invalid email format.
    The server should respond with a 422 Unprocessable Entity status code.
    """
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "invalid-email",   # Invalid email format
            "password": "Testpassword123!"
        }
    )
    assert response.status_code == 422, "Expected status code 422 for invalid email format"
    
    json_response = response.json()
    assert json_response["success"] is False, "Expected success to be False for invalid email format"
    assert json_response["error_code"] == "VALIDATION_ERROR", "Expected error code for validation error"
    assert "Input validation failed" in json_response["message"], "Expected validation error message"
    assert isinstance(json_response["detail"], list), "Expected detail to be a list of errors"

def test_region_invalid_password():
    """
    Test registration with a password that does not meet complexity requirements.
    Example: all lowercase letters and lacking a digit and special character.
    The server should respond with a 422 Unprocessable Entity status code.
    """
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password"  # Weak password
        }
    )
    assert response.status_code == 422, "Expected status code 422 for weak password"
    json_response = response.json()
    assert json_response["success"] is False, "Expected success to be False for weak password"
    assert json_response["error_code"] == "VALIDATION_ERROR", "Expected error code for validation error"
    assert "Input validation failed" in json_response["message"], "Expected validation error message"
    assert isinstance(json_response["detail"], list), "Expected detail to be a list of errors"
    

def test_registration_short_username():
    """
    Test registration with a username that is too short.
    The server should respond with a 422 Unprocessable Entity status code.
    """
    response = client.post(
        "/auth/register",
        json={
            "username": "ab",  # Too short username
            "email": "test@example.com",
            "password": "Testpassword123!"
        }
    )
    assert response.status_code == 422, "Expected status code 422 for short username"
    json_response = response.json()
    assert json_response["success"] is False, "Expected success to be False for short username"
    assert json_response["error_code"] == "VALIDATION_ERROR", "Expected error code for validation error"
    assert "Input validation failed" in json_response["message"], "Expected validation error message"
    assert isinstance(json_response["detail"], list), "Expected detail to be a list of errors"

# endregion Registration Validation Tests



# region Update Validation Tests

@pytest.fixture(scope="module")
def create_test_user():
    """
    Fixture to create a valid token header for update validation tests.
    """
    # Register a test user
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser2",
            "email": "validation@example.com",
            "password": "Testpassword123!"
        }
    )
    assert response.status_code == 201, "Failed to create test user"
    # Log in to obtain an access token
    login_response = client.post(
        "/auth/login",
        data={
            "username": "testuser2",
            "password": "Testpassword123!"
        }
    )
    assert login_response.status_code == 200, "Failed to log in to obtain access token"
    token = login_response.json().get("access_token")
    assert token is not None, "Failed to obtain access token"
    return {"Authorization": f"Bearer {token}"}


def test_profile_update_invalid_email(create_test_user):
    """
    Test updating the profile with an invalid email format.
    The server should respond with a 422 Unprocessable Entity status code.
    """
    response = client.put(
        "/users/profile",
        headers=create_test_user,
        json={"email": "invalid-email"}  # Invalid email format
    )
    assert response.status_code == 422, "Expected status code 422 for invalid email format"
    json_response = response.json()
    assert json_response["success"] is False, "Expected success to be False for invalid email format"
    assert json_response["error_code"] == "VALIDATION_ERROR", "Expected error code for validation error"
    assert "Input validation failed" in json_response["message"], "Expected validation error message"
    assert isinstance(json_response["detail"], list), "Expected detail to be a list of errors"
    

def test_profile_update_valid(create_test_user):
    """
    Test updating the profile with valid data.
    The server should respond with a 200 OK status code and return the updated user data.
    """
    update_payload = {
        "username": "updatedvalidationuser",
        "email": "updated_validation@example.com"
    }
    response = client.put(
        "/users/profile",
        headers=create_test_user,
        json=update_payload
    )
    assert response.status_code == 200, "Expected status code 200 for valid profile update"
    data = response.json()
    assert data["username"] == update_payload["username"], "Expected updated username"
    assert data["email"] == update_payload["email"], "Expected updated email"
    
    
# def test_invalid_email_verification(create_test_user):
#     """
#     Test email verification with an invalid token.
#     The server should respond with a 422 Unprocessable Entity status code.
#     """
#     response = client.post(
#         "/auth/verify-email",
#         headers=create_test_user,
#         json={"token": "invalid-token"}  # Invalid token
#     )
#     assert response.status_code == 422, "Expected status code 422 for invalid token"
#     json_response = response.json()
#     assert json_response["success"] is False, "Expected success to be False for invalid token"
#     assert json_response["error_code"] == "VALIDATION_ERROR", "Expected error code for validation error"
#     assert "Input validation failed" in json_response["message"], "Expected validation error message"
#     assert isinstance(json_response["detail"], list), "Expected detail to be a list of errors"
    

# def test_valid_email_verification(create_test_user):
#     """
#     Test email verification with a valid token.
#     The server should respond with a 200 OK status code and a success message.
#     """
#     # Assuming the token is valid for the test user
#     response = client.post(
#         "/auth/verify-email",
#         headers=create_test_user,
#         json={"token": "valid-token"}  # Valid token (for testing purposes)
#     )
#     assert response.status_code == 200, "Expected status code 200 for valid email verification"
#     json_response = response.json()
#     assert json_response["success"] is True, "Expected success to be True for valid email verification"
#     assert json_response["message"] == "Email verified successfully", "Expected success message"

# endregion Update Validation Tests