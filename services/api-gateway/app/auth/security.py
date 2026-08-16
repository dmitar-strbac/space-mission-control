from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.auth.models import AuthenticatedUser, UserRole
from app.core.config import Settings, get_settings

password_hash = PasswordHash.recommended()


class AuthenticationError(Exception):
    pass


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def authenticate_user(
    username: str,
    password: str,
    settings: Settings | None = None,
) -> AuthenticatedUser | None:
    resolved_settings = settings or get_settings()

    users = {
        resolved_settings.operator_username: (
            resolved_settings.operator_password_hash,
            UserRole.OPERATOR,
        ),
        resolved_settings.observer_username: (
            resolved_settings.observer_password_hash,
            UserRole.OBSERVER,
        ),
    }

    credentials = users.get(username)

    if credentials is None:
        return None

    hashed_password, role = credentials

    if not verify_password(
        password,
        hashed_password,
    ):
        return None

    return AuthenticatedUser(
        username=username,
        role=role,
    )


def create_access_token(
    user: AuthenticatedUser,
    settings: Settings | None = None,
) -> str:
    resolved_settings = settings or get_settings()

    issued_at = datetime.now(UTC)
    expires_at = issued_at + timedelta(minutes=(resolved_settings.jwt_access_token_expire_minutes))

    payload = {
        "sub": user.username,
        "role": user.role.value,
        "iat": issued_at,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        resolved_settings.jwt_secret_key,
        algorithm=resolved_settings.jwt_algorithm,
    )


def decode_access_token(
    token: str,
    settings: Settings | None = None,
) -> AuthenticatedUser:
    resolved_settings = settings or get_settings()

    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            resolved_settings.jwt_secret_key,
            algorithms=[
                resolved_settings.jwt_algorithm,
            ],
        )
    except InvalidTokenError as exc:
        raise AuthenticationError("Invalid or expired access token.") from exc

    username = payload.get("sub")
    role_value = payload.get("role")

    if not isinstance(username, str):
        raise AuthenticationError("Access token is missing a valid subject.")

    if not isinstance(role_value, str):
        raise AuthenticationError("Access token is missing a valid role.")

    try:
        role = UserRole(role_value)
    except ValueError as exc:
        raise AuthenticationError("Access token contains an invalid role.") from exc

    return AuthenticatedUser(
        username=username,
        role=role,
    )
