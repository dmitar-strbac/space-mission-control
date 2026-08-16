from enum import StrEnum

from pydantic import BaseModel


class UserRole(StrEnum):
    OPERATOR = "OPERATOR"
    OBSERVER = "OBSERVER"


class AuthenticatedUser(BaseModel):
    username: str
    role: UserRole


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int


class CurrentUserResponse(BaseModel):
    username: str
    role: UserRole
