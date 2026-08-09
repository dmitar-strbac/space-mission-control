from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    InvalidSimulationTransitionError,
    SimulationAlreadyExistsError,
    SimulationError,
    SimulationNotFoundError,
    SimulationStateUnavailableError,
)


def register_exception_handlers(
    app: FastAPI,
) -> None:
    @app.exception_handler(SimulationError)
    async def handle_simulation_error(
        _: Request,
        exc: SimulationError,
    ) -> JSONResponse:
        status_code = status.HTTP_400_BAD_REQUEST

        if isinstance(
            exc,
            SimulationNotFoundError,
        ):
            status_code = status.HTTP_404_NOT_FOUND

        elif isinstance(
            exc,
            (
                InvalidSimulationTransitionError,
                SimulationAlreadyExistsError,
            ),
        ):
            status_code = status.HTTP_409_CONFLICT

        elif isinstance(
            exc,
            SimulationStateUnavailableError,
        ):
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE

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
