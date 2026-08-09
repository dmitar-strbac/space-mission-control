from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    InvalidMissionTransitionError,
    MissionError,
    MissionNotFoundError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(MissionError)
    async def handle_mission_error(_: Request, exc: MissionError) -> JSONResponse:
        status_code = status.HTTP_400_BAD_REQUEST
        if isinstance(exc, MissionNotFoundError):
            status_code = status.HTTP_404_NOT_FOUND
        elif isinstance(exc, InvalidMissionTransitionError):
            status_code = status.HTTP_409_CONFLICT

        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )
