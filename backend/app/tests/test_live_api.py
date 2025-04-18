import pytest
import httpx

BASE_URL = "http://localhost:8000" 

@pytest.mark.order(1)
def test_ping():
    """
    Test the ping endpoint.
    """
    r = httpx.get(f"{BASE_URL}/api/ping")
    assert r.status_code == 200
    assert r.json() == {"message": "Pong!"}
    
@pytest.mark.order(2)
def test_register_and_login_profile():
    """
    Test the registration and login of a user profile.
    """
    # Register a new user
    payload = {
        "username": "testuser",
        "email": "testuser@test.com",
        "password": "TestPassword!123"
    }
    r = httpx.post(f"{BASE_URL}/auth/register", json=payload)
    assert r.status_code == 201
    # Login with the new user
    data = {
        "username": "testuser",
        "password": "TestPassword!123"
    }
    r = httpx.post(f"{BASE_URL}/auth/login", data=data)
    assert r.status_code == 200
    token_data = r.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    
@pytest.mark.order(3)
def test_duplicate_registration():
    """
    Test the registration of a duplicate user.
    """
    # Register user with the same username as before
    payload = {
        "username": "testuser",
        "email": "duplicate@test.com",
        "password": "TestPassword!123"
    }
    r = httpx.post(f"{BASE_URL}/auth/register", json=payload)
    assert r.status_code == 400
    err = r.json()
    assert err["success"] is False
    assert err["message"] == "Username already registered"
    assert err["error_code"] == "HTTP_ERROR"
    # Register user with the same email as before
    payload = {
        "username": "newuser",
        "email": "testuser@test.com",
        "password": "TestPassword!123"
    }
    r = httpx.post(f"{BASE_URL}/auth/register", json=payload)
    assert r.status_code == 400
    err = r.json()
    assert err["success"] is False
    assert err["message"] == "Email already registered"
    assert err["error_code"] == "HTTP_ERROR"
    
@pytest.mark.order(4)
def test_invalid_login():
    """
    Test the login with invalid credentials.
    """
    # Invalid username and password
    data = {
        "username": "invaliduser",
        "password": "InvalidPassword!123"
    }
    r = httpx.post(f"{BASE_URL}/auth/login", data=data)
    assert r.status_code == 401
    err = r.json()
    assert err["success"] is False
    assert err["message"] == "Incorrect username or password"
    # Invalid password for existing user
    data = {
        "username": "testuser",
        "password": "InvalidPassword!123"
    }
    r = httpx.post(f"{BASE_URL}/auth/login", data=data)
    assert r.status_code == 401
    err = r.json()
    assert err["success"] is False
    assert err["message"] == "Incorrect username or password"
    
@pytest.mark.order(5)
@pytest.mark.parametrize(
    "payload, field", [
        ({"email": "usernametest@test.com", "password": "TestPassword!123"}, "username"),
        ({"username": "emailtest", "password": "TestPassword!123"}, "email"),
        ({"username": "passwordtest", "email": "passwordtest@test.com"}, "password"),
        ({"username": "ab", "email": "shortusernametest@test.com", "password": "TestPassword!123"}, "username"),
        ({"username": "invemailtest", "email": "invalidemail", "password": "TestPassword!123"}, "email"),
        ({"username": "weakpasstest", "email": "weakpass@test.com", "password": "weak"}, "password"),
    ]
)
def test_register_validation_errors(payload, field):
    """
    Test the registration endpoint with various validation errors.
    """
    r = httpx.post(f"{BASE_URL}/auth/register", json=payload)
    assert r.status_code == 422
    detail = r.json()["detail"]
    # Check if the error message contains the expected field
    assert any(field in err["loc"] for err in detail)
    
@pytest.mark.order(6)
def test_login_nonexistent_and_wrong_password():
    """
    Test the login with a non-existent user and wrong password.
    """
    # Non-existent user
    r = httpx.post(
        f"{BASE_URL}/auth/login", 
        data={
            "username": "nonexistentuser", 
            "password": "TestPassword!123"
        }
    )
    assert r.status_code == 401
    # Wrong password for existing user
    payload = {
        "username": "wrongpassworduser",
        "email": "wrongpass@test.com",
        "password": "TestPassword!123"
    }
    r = httpx.post(f"{BASE_URL}/auth/register", json=payload)
    assert r.status_code == 201
    r = httpx.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": "wrongpassworduser",
            "password": "WrongPassword!123"
        }
    )
    assert r.status_code == 401
    
@pytest.mark.order(7)
def test_profile_access_without_and_with_invalid_token():
    """
    Test accessing the profile endpoint without a token and with an invalid token.
    """
    # Access without token
    r = httpx.get(f"{BASE_URL}/users/profile")
    assert r.status_code == 401
    # Access with invalid token
    headers = {"Authorization": "Bearer invalidtoken"}
    r = httpx.get(f"{BASE_URL}/users/profile", headers=headers)
    assert r.status_code == 401
    
@pytest.mark.order(8)
def test_profile_read_and_update():
    """
    Test reading and updating the user profile.
    """
    # Register and login a user
    payload = {
        "username": "readandupdatetest",
        "email": "readandupdate@test.com",
        "password": "TestPassword!123"
    }
    r = httpx.post(f"{BASE_URL}/auth/register", json=payload)
    assert r.status_code == 201
    data = {
        "username": "readandupdatetest",
        "password": "TestPassword!123"
    }
    r = httpx.post(f"{BASE_URL}/auth/login", data=data)
    assert r.status_code == 200
    hdr = {"Authorization": f"Bearer {r.json()['access_token']}"}
    # Read profile
    r = httpx.get(f"{BASE_URL}/users/profile", headers=hdr)
    assert r.status_code == 200
    profile = r.json()
    assert profile["username"] == "readandupdatetest"
    assert profile["email"] == "readandupdate@test.com"
    # Update profile
    update = {
        "username": "updateduser",
        "email": "updatedemail@test.com"
    }
    r = httpx.put(f"{BASE_URL}/users/profile", headers=hdr, json=update)
    assert r.status_code == 200
    updated_profile = r.json()
    assert updated_profile["username"] == "updateduser"
    assert updated_profile["email"] == "updatedemail@test.com"
    # Attempt to update to a duplicate username
    # Register another user
    payload = {
        "username": "anotheruser",
        "email": "anotheruser@test.com",
        "password": "TestPassword!123"
    }
    r = httpx.post(f"{BASE_URL}/auth/register", json=payload)
    assert r.status_code == 201
    
    # Update with duplicate username 
    data = {
        "username": "updateduser",
        "password": "TestPassword!123"
    }
    r = httpx.post(f"{BASE_URL}/auth/login", data=data)
    assert r.status_code == 200
    hdr = {"Authorization": f"Bearer {r.json()['access_token']}"}
    duplicate_update = {
        "username": "anotheruser",
    }
    r = httpx.put(f"{BASE_URL}/users/profile", headers=hdr, json=duplicate_update)
    assert r.status_code == 400
    err = r.json()
    assert err["success"] is False
    assert err["message"] == "Username already registered"
    
@pytest.mark.order(9)
def test_verify_email_invalid_token():
    """
    Test the email verification with an invalid token.
    """
    # Invalid token
    r = httpx.post(f"{BASE_URL}/auth/verify-email?token=invalidtoken")
    assert r.status_code == 400
    err = r.json()
    assert err["success"] is False
    assert err["message"] == "Invalid or expired verification token"