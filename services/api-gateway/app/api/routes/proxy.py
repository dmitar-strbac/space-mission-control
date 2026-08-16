import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from app.clients.registry import ServiceRegistry
from app.clients.service_client import ServiceClient

router = APIRouter(
    prefix="/api",
    tags=["Gateway"],
)

_ALLOWED_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
]

_REQUEST_HEADERS_TO_EXCLUDE = {
    "connection",
    "content-length",
    "host",
}

_RESPONSE_HEADERS_TO_EXCLUDE = {
    "connection",
    "content-encoding",
    "content-length",
    "transfer-encoding",
}


def _forward_headers(request: Request) -> dict[str, str]:
    return {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in _REQUEST_HEADERS_TO_EXCLUDE
    }


@router.api_route(
    "/{service_route}",
    methods=_ALLOWED_METHODS,
)
@router.api_route(
    "/{service_route}/{path:path}",
    methods=_ALLOWED_METHODS,
)
async def proxy_request(
    service_route: str,
    request: Request,
    path: str = "",
) -> Response:
    registry: ServiceRegistry = request.app.state.service_registry
    target = registry.get(service_route)

    if target is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "UNKNOWN_GATEWAY_ROUTE",
                    "message": (f"Unknown gateway service route: {service_route}."),
                    "service": "api-gateway",
                }
            },
        )

    client: httpx.AsyncClient = request.app.state.http_client
    service_client = ServiceClient(client)

    response = await service_client.request(
        target=target,
        method=request.method,
        path=path,
        headers=_forward_headers(request),
        query_params=httpx.QueryParams(str(request.query_params)),
        body=await request.body(),
    )

    response_headers = {
        key: value
        for key, value in response.headers.items()
        if key.lower() not in _RESPONSE_HEADERS_TO_EXCLUDE
    }

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=response_headers,
    )
