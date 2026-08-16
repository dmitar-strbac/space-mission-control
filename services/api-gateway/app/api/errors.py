from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.clients.service_client import (
    DownstreamServiceTimeoutError,
    DownstreamServiceUnavailableError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DownstreamServiceTimeoutError)
    async def handle_downstream_timeout(
        _: Request,
        exc: DownstreamServiceTimeoutError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={
                "error": {
                    "code": "DOWNSTREAM_TIMEOUT",
                    "message": (
                        f"{exc.service_name} did not respond within the configured timeout."
                    ),
                    "service": exc.service_name,
                }
            },
        )

    @app.exception_handler(DownstreamServiceUnavailableError)
    async def handle_downstream_unavailable(
        _: Request,
        exc: DownstreamServiceUnavailableError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": {
                    "code": "DOWNSTREAM_UNAVAILABLE",
                    "message": (f"{exc.service_name} is currently unavailable."),
                    "service": exc.service_name,
                }
            },
        )
