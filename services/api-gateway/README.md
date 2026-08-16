# 🌐 API Gateway

The API Gateway is the single entry point for client communication with the Space Mission Control backend.

## Responsibilities

- JWT authentication
- Role-based authorization
- HTTP routing to backend microservices
- WebSocket proxying for real-time telemetry
- Response and infrastructure error normalization
- Aggregated service health checks
- Request timeout handling
- Circuit breaker protection

## Authentication

The API Gateway authenticates frontend clients using signed JWT access tokens.

Two roles are supported:

- `OPERATOR` — full mission-control access, including state-changing operations
- `OBSERVER` — read-only access to mission data and real-time telemetry

Authentication endpoints:

```text
POST /auth/login
GET /auth/me
```

All `/api/*` routes require authentication.

State-changing requests require the `OPERATOR` role, while authenticated `OBSERVER` users may perform read-only requests.

Real-time telemetry WebSocket connections also require a valid access token.

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
