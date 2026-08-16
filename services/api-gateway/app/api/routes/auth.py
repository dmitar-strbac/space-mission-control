from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.auth.models import (
    AuthenticatedUser,
    CurrentUserResponse,
    LoginRequest,
    TokenResponse,
)
from app.auth.security import (
    authenticate_user,
    create_access_token,
)
from app.core.config import get_settings

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
) -> TokenResponse:
    user = authenticate_user(
        request.username,
        request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    settings = get_settings()

    return TokenResponse(
        access_token=create_access_token(user),
        expires_in_seconds=(settings.jwt_access_token_expire_minutes * 60),
    )


@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
def get_me(
    user: Annotated[
        AuthenticatedUser,
        Depends(get_current_user),
    ],
) -> CurrentUserResponse:
    return CurrentUserResponse(
        username=user.username,
        role=user.role,
    )
