from fastapi.testclient import TestClient
from backend.main import app, fake_users_db

client = TestClient(app)

def test_ping():
    response = client.get("/api/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_registration_and_login():
    # Clear fake database to ensure a clean test environment
    fake_users_db.clear()

    # Register a new user
    registration_response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )

    assert registration_response.status_code == 201
    assert registration_response.json()["msg"] == "User registered successfully"

    # Login with the new user credentials
    login_response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )

    assert login_response.status_code == 200

    token_data = login_response.json()
    assert "access_token" in token_data

    # Test accessing the protected profile endpoint using the token
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    profile_response = client.get("/users/profile", headers=headers)

    assert profile_response.status_code == 200

    user_data = profile_response.json()
    assert user_data["username"] == "testuser"