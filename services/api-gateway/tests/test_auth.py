from fastapi.testclient import TestClient

from app.main import app


def test_operator_can_login() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/auth/login",
            json={
                "username": "operator",
                "password": "operator123",
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert isinstance(
        payload["access_token"],
        str,
    )
    assert payload["token_type"] == "bearer"
    assert payload["expires_in_seconds"] == 3600


def test_observer_can_login() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/auth/login",
            json={
                "username": "observer",
                "password": "observer123",
            },
        )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_invalid_credentials_are_rejected() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/auth/login",
            json={
                "username": "operator",
                "password": "wrong-password",
            },
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password."}


def test_current_user_returns_authenticated_operator() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/auth/login",
            json={
                "username": "operator",
                "password": "operator123",
            },
        )

        token = login_response.json()["access_token"]

        response = client.get(
            "/auth/me",
            headers={"Authorization": (f"Bearer {token}")},
        )

    assert response.status_code == 200

    assert response.json() == {
        "username": "operator",
        "role": "OPERATOR",
    }


def test_current_user_requires_authentication() -> None:
    with TestClient(app) as client:
        response = client.get("/auth/me")

    assert response.status_code == 401


def test_invalid_access_token_is_rejected() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/auth/me",
            headers={"Authorization": ("Bearer invalid-token")},
        )

    assert response.status_code == 401
