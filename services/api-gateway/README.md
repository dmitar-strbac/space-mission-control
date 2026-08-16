# 🌐 API Gateway

The API Gateway is the single entry point for client communication with the Space Mission Control backend.

## Responsibilities

- HTTP routing to backend microservices
- WebSocket proxying for real-time telemetry
- Authentication and authorization
- Response and infrastructure error normalization
- Aggregated service health checks
- Request timeout handling
- Circuit breaker protection

## Service Routing

| Gateway Path             | Downstream Service         |
| ------------------------ | -------------------------- |
| `/api/mission/*`         | Mission Service            |
| `/api/vehicle/*`         | Vehicle Service            |
| `/api/trajectory/*`      | Trajectory Service         |
| `/api/flight-dynamics/*` | Flight Dynamics Service    |
| `/api/communication/*`   | Communication Service      |
| `/api/telemetry/*`       | Telemetry & Safety Service |

Real-time telemetry is exposed through:

```text
/ws/missions/{mission_id}/telemetry
```

The Gateway proxies this WebSocket connection to the Telemetry & Safety Service.

## Resilience

Synchronous downstream requests use configurable timeouts and per-service circuit breakers.

A circuit breaker opens after repeated downstream failures and temporarily prevents additional requests until the recovery interval expires.

The aggregated health endpoint is available at:

```text
GET /health/services
```

## Technology

- Python
- FastAPI
- HTTPX
- WebSockets

## Default Port

`8000`
