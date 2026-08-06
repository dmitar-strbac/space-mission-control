from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    InvalidManualStatusError,
    SpacecraftDeletionConflictError,
    SpacecraftModificationConflictError,
    SpacecraftNameConflictError,
    SpacecraftNotFoundError,
)


def error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(SpacecraftNotFoundError)
    async def handle_not_found(
        _: Request,
        error: SpacecraftNotFoundError,
    ) -> JSONResponse:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            code="SPACECRAFT_NOT_FOUND",
            message=str(error),
            details={
                "spacecraft_id": str(error.spacecraft_id),
            },
        )

    @app.exception_handler(SpacecraftNameConflictError)
    async def handle_name_conflict(
        _: Request,
        error: SpacecraftNameConflictError,
    ) -> JSONResponse:
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            code="SPACECRAFT_NAME_CONFLICT",
            message=str(error),
            details={
                "name": error.name,
            },
        )

    @app.exception_handler(SpacecraftDeletionConflictError)
    async def handle_deletion_conflict(
        _: Request,
        error: SpacecraftDeletionConflictError,
    ) -> JSONResponse:
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            code="SPACECRAFT_DELETION_CONFLICT",
            message=str(error),
            details={
                "spacecraft_id": str(error.spacecraft_id),
                "status": error.status.value,
            },
        )

    @app.exception_handler(SpacecraftModificationConflictError)
    async def handle_modification_conflict(
        _: Request,
        error: SpacecraftModificationConflictError,
    ) -> JSONResponse:
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            code="SPACECRAFT_MODIFICATION_CONFLICT",
            message=str(error),
            details={
                "spacecraft_id": str(error.spacecraft_id),
                "status": error.status.value,
            },
        )

    @app.exception_handler(InvalidManualStatusError)
    async def handle_invalid_status(
        _: Request,
        error: InvalidManualStatusError,
    ) -> JSONResponse:
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            code="INVALID_MANUAL_SPACECRAFT_STATUS",
            message=str(error),
            details={
                "status": error.status.value,
            },
        )
