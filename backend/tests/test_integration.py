from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)

def test_complete_user_flow():
    """
    Test the complete user flow: registration, login, and token generation.
    """

    # region Step 1: Register a new user

    register_response = client.post(
        "/auth/register",
        json={
            "username": "integrationuser",
            "email": "integration@example.com",
            "password": "integrationpassword"
        }
    )
    assert register_response.status_code == 201, f"User registration failed: f{register_response.json()}"

    # endregion Step 1: Register a new user



    # region Step 2: Login with the registered user

    login_response = client.post(
        "/auth/login",
        data={
            "username": "integrationuser",
            "password": "integrationpassword"
        }
    )
    assert login_response.status_code == 200, f"User login failed: {login_response.json()}"
    
    token = login_response.json().get("access_token")
    assert token is not None, "No access token provided on login."

    headers = {"Authorization": f"Bearer {token}"}

    # endregion Step 2: Login with the registered user



    # region Step 3: Access protected profile endpoint with the token

    profile_response = client.get("/users/profile", headers=headers)
    assert profile_response.status_code == 200, f"Accessing profile failed: {profile_response.json()}"

    profile_data = profile_response.json()
    assert profile_data["username"] == "integrationuser", "Profile username mismatch."

    # endregion Step 3: Access protected profile endpoint with the token



    # region Step 4: Update user profile

    update_payload = {
        "username": "integrationuser_updated",
        "email": "integration_updated@example.com"
    }
    update_response = client.put("/users/profile", headers=headers, json=update_payload)
    assert update_response.status_code == 200, f"Profile update failed: {update_response.json()}"

    updated_profile_data = update_response.json()
    assert updated_profile_data["username"] == "integrationuser_updated", "Profile update username mismatch."
    assert updated_profile_data["email"] == "integration_updated@example.com", "Profile update email mismatch."

    # endregion Step 4: Update user profile



    # region Step 5: Fetch the profile again to confirm the update

    confirm_response = client.get("/users/profile", headers=headers)
    assert confirm_response.status_code == 200, f"Confirming profile update failed: {confirm_response.json()}"
    confirm_profile_data = confirm_response.json()
    assert confirm_profile_data["username"] == "integrationuser_updated", "Confirmed profile username mismatch."
    assert confirm_profile_data["email"] == "integration_updated@example.com", "Confirmed profile email mismatch."

    # endregion Step 5: Fetch the profile again to confirm the update  