import pytest
from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)

# region Pytest Fixtures Setup

@pytest.fixture(scope="module")
def test_user():
    """
    Registers a new test user.
    Since the tests run agains an in-memory or test database, this user will not persist. 
    """
    response = client.post(
        "/auth/register",
        json={
            "username": "validationuser",
            "email": "validation@example.com",
            "password": "Testpassword123!"
        }
    )
    assert response.status_code == 201, "User registration failed"
    return {"username": "testuser", "password": "Testpassword123!"}


@pytest.fixture(scope="module")
def token_header(test_user):
    """
    Logs in the test user to obtain valid JWT token.
    Returns an HTTP header with the Authorization token set.
    """
    login_response = client.post(
        "/auth/login",
        data={
            "username": "validationuser",
            "password": "Testpassword123!"
        }
    )
    assert login_response.status_code == 200, "Failed to log in to obtain access token"
    token = login_response.json().get("access_token")
    assert token is not None, "Failed to obtain access token"
    return {"Authorization": f"Bearer {token}"}

# endregion Pytest Fixtures Setup


def test_access_protected_endpoint_without_token():
    """
    Test that attempting to access the protected user profile endpoint
    without a valid token returns a 401 Unauthorized response.
    """
    response = client.get("/users/profile")
    assert response.status_code == 401, "Access without token should return 401"
    assert response.json()["message"] == "Not authenticated", "Expected authentication error message"


def test_access_protected_endpoint_with_token(token_header):
    """
    Test that accessing the protected user profile endpoint with a valid token
    returns user profile successfully.
    """
    response = client.get("/users/profile", headers=token_header)
    assert response.status_code == 200, "Valid token did not grant access to profile" 
    data = response.json()
    assert data["username"] == "validationuser", "Returned profile data is incorrect"


def test_update_protected_endpoint_without_token():
    """
    Test that attempting to update the user profile without a valid token
    returns a 401 Unauthorized response.
    """
    response = client.put(
        "/users/profile",
        json={"username": "newusername", "email": "new@example.com"}
    )
    assert response.status_code == 401, "Access without token should return 401"
    assert response.json()["message"] == "Not authenticated", "Expected authentication error message"


def test_update_protected_endpoint_with_token(token_header):
    """
    Test that updating the user profile with a valid token succeeds
    and changes are reflected in the response.
    """
    update_payload = {
        "username": "newusername",
        "email": "new@example.com"
    }
    response = client.put(
        "/users/profile",
        headers=token_header,
        json=update_payload
    )
    assert response.status_code == 200, "Valid token did not grant access to update profile"
    updated_data = response.json()
    assert updated_data["username"] == update_payload["username"], "Username was not updated correctly"
    assert updated_data["email"] == update_payload["email"], "Email was not updated correctly"