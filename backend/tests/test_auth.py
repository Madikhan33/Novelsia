import pytest
from fastapi.testclient import TestClient


def test_register_user(client: TestClient, test_user_data: dict):
    """
    Тест регистрации нового пользователя.
    """
    response = client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 200
    assert response.json()["username"] == test_user_data["username"]
    assert response.json()["email"] == test_user_data["email"]
    assert response.json()["is_active"] == True
    assert response.json()["is_verified"] == False
    assert response.json()["created_at"] is not None

def test_login_user(client: TestClient, test_user_data: dict):
    """
    Тест входа пользователя.
    """
    response = client.post("/api/auth/login", data={"username": test_user_data["username"], "password": test_user_data["password"]})
    assert response.status_code == 200
    assert response.json()["access_token"] is not None
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(client: TestClient):
    """
    Тест входа с неверными учетными данными.
    """
    response = client.post("/api/auth/login", data={"username": "invalid_username", "password": "invalid_password"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_refresh_token(client: TestClient, test_user_data: dict):
    """
    Тест обновления JWT токена.
    """
    response = client.post("/api/auth/login", data={"username": test_user_data["username"], "password": test_user_data["password"]})
    assert response.status_code == 200
    assert response.json()["access_token"] is not None
    assert response.json()["token_type"] == "bearer"
    refresh_token = response.json()["refresh_token"]
    response = client.post("/api/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert response.status_code == 200

def test_logout(client: TestClient, test_user_data: dict):
    """
    Тест выхода пользователя.
    """
    response = client.post("/api/auth/login", data={"username": test_user_data["username"], "password": test_user_data["password"]})
    assert response.status_code == 200
    assert response.json()["access_token"] is not None
    assert response.json()["token_type"] == "bearer"
    response = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {response.json()['access_token']}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"

def test_forgot_password(client: TestClient, test_user_data: dict):
    """
    Тест запроса сброса пароля.
    """
    response = client.post("/api/auth/forgot-password", json={"email": test_user_data["email"]})
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset instructions sent to email"

def test_reset_password(client: TestClient, test_user_data: dict):
    """
    Тест сброса пароля.
    """
    response = client.post("/api/auth/forgot-password", json={"email": test_user_data["email"]})
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset instructions sent to email"
    token = response.json()["token"]
    response = client.post("/api/auth/reset-password", json={"token": token, "new_password": "new_password"})
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset successfully"

def test_verify_email(client: TestClient, test_user_data: dict):
    """
    Тест подтверждения email.
    """
    response = client.post("/api/auth/forgot-password", json={"email": test_user_data["email"]})
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset instructions sent to email"
    token = response.json()["token"]
    response = client.post("/api/auth/verify-email", json={"token": token})
    assert response.status_code == 200
    assert response.json()["message"] == "Email verified successfully"