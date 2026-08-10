from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    CommandDeliveryError,
    CommandNotFoundError,
    CommunicationError,
    CommunicationProfileAlreadyExistsError,
    CommunicationProfileNotFoundError,
    InvalidCommandTransitionError,
)


def register_exception_handlers(
    app: FastAPI,
) -> None:
    @app.exception_handler(CommunicationError)
    async def handle_communication_error(
        _: Request,
        exc: CommunicationError,
    ) -> JSONResponse:
        status_code = status.HTTP_400_BAD_REQUEST

        if isinstance(
            exc,
            (
                CommandNotFoundError,
                CommunicationProfileNotFoundError,
            ),
        ):
            status_code = status.HTTP_404_NOT_FOUND

        elif isinstance(
            exc,
            (
                InvalidCommandTransitionError,
                CommunicationProfileAlreadyExistsError,
            ),
        ):
            status_code = status.HTTP_409_CONFLICT

        elif isinstance(
            exc,
            CommandDeliveryError,
        ):
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
