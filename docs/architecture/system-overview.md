# 🏗️ System Overview

Space Mission Control is organized as a distributed microservice platform where each service owns its data, exposes well-defined APIs and communicates through REST and asynchronous messaging.

---

## ⚙️ Application Components

| Component                  | Port | Database   |
| -------------------------- | ---: | ---------- |
| API Gateway                | 8000 | —          |
| Mission Service            | 8001 | PostgreSQL |
| Vehicle Service            | 8002 | PostgreSQL |
| Trajectory Service         | 8003 | PostgreSQL |
| Flight Dynamics Service    | 8004 | PostgreSQL |
| Communication Service      | 8005 | PostgreSQL |
| Telemetry & Safety Service | 8006 | MongoDB    |
| Frontend                   | 5173 | —          |

---

## 📡 Communication

The platform combines synchronous and asynchronous communication patterns.

### REST

REST is used for:

- Frontend requests
- CRUD operations
- Synchronous service interactions

### NATS JetStream

NATS JetStream is used for reliable event-driven communication, including:

- Mission preparation Saga steps
- Mission lifecycle events
- Spacecraft commands
- Safety alerts
- Emergency abort events

### NATS Publish/Subscribe

Standard NATS messaging is used for high-frequency simulation updates where long-term persistence is not required.

### WebSocket

WebSocket communication delivers live telemetry, mission status updates and safety alerts to the frontend.

---

## 🗄️ Data Ownership

Each microservice owns its database and is responsible for managing its own data.

Direct database access between services is not allowed. All communication must occur through REST APIs or asynchronous messaging.
