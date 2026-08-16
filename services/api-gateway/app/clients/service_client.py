from collections.abc import Mapping

import httpx
from httpx import QueryParams

from app.clients.registry import ServiceTarget
from app.resilience.circuit_breaker import CircuitBreakerOpenError


class DownstreamServiceUnavailableError(Exception):
    def __init__(self, service_name: str) -> None:
        self.service_name = service_name
        super().__init__(f"{service_name} is unavailable")


class DownstreamServiceTimeoutError(Exception):
    def __init__(self, service_name: str) -> None:
        self.service_name = service_name
        super().__init__(f"{service_name} timed out")


class ServiceClient:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def request(
        self,
        *,
        target: ServiceTarget,
        method: str,
        path: str,
        headers: Mapping[str, str],
        query_params: QueryParams,
        body: bytes,
    ) -> httpx.Response:
        try:
            await target.circuit_breaker.before_request()
        except CircuitBreakerOpenError as exc:
            raise DownstreamServiceUnavailableError(target.name) from exc

        url = f"{target.base_url}/{path.lstrip('/')}"

        try:
            response = await self._client.request(
                method=method,
                url=url,
                headers=headers,
                params=query_params,
                content=body,
            )
        except httpx.TimeoutException as exc:
            await target.circuit_breaker.record_failure()
            raise DownstreamServiceTimeoutError(target.name) from exc
        except httpx.RequestError as exc:
            await target.circuit_breaker.record_failure()
            raise DownstreamServiceUnavailableError(target.name) from exc

        if response.status_code >= 500:
            await target.circuit_breaker.record_failure()
        else:
            await target.circuit_breaker.record_success()

        return response
