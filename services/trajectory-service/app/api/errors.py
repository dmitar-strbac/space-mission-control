from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    TrajectoryError,
    TrajectoryPlanNotFoundError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(TrajectoryError)
    async def handle_trajectory_error(
        _: Request,
        exc: TrajectoryError,
    ) -> JSONResponse:
        status_code = status.HTTP_400_BAD_REQUEST

        if isinstance(exc, TrajectoryPlanNotFoundError):
            status_code = status.HTTP_404_NOT_FOUND

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
