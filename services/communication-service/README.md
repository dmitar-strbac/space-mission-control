# 📡 Communication Service

The Communication Service is responsible for spacecraft communication profiles, signal-delay simulation and command delivery tracking.

## Responsibilities

- Create and manage mission communication profiles
- Calculate distance-based one-way signal propagation delay
- Simulate additional network latency
- Simulate configurable packet loss
- Handle complete communication interruptions
- Manage spacecraft command lifecycle and delivery
- Track command reception, execution, rejection, expiration and loss
- Persist command audit history using PostgreSQL and SQLAlchemy
- Manage database schema through Alembic migrations
- Provide unit and integration test coverage

> **Note:** NATS-based command delivery, Prepare Mission Saga integration, corrective-maneuver events and Emergency Abort event flows are implemented separately in later features. This branch provides the communication domain model and persistence required for those distributed workflows.

## API

| Method | Route                                  | Purpose                             |
| ------ | -------------------------------------- | ----------------------------------- |
| POST   | `/communication-profiles`              | Create a communication profile      |
| GET    | `/communication-profiles/{mission_id}` | Get a mission communication profile |
| PATCH  | `/communication-profiles/{mission_id}` | Update communication conditions     |
| POST   | `/commands`                            | Create a spacecraft command         |
| GET    | `/commands/{command_id}`               | Get a command                       |
| GET    | `/missions/{mission_id}/commands`      | List commands for a mission         |
| GET    | `/commands/{command_id}/logs`          | Get command audit history           |
| POST   | `/commands/{command_id}/queue`         | Queue a command for transmission    |
| POST   | `/commands/{command_id}/dispatch`      | Begin command transmission          |
| POST   | `/commands/{command_id}/deliver`       | Confirm command delivery            |
| POST   | `/commands/{command_id}/execute`       | Confirm command execution           |
| POST   | `/commands/{command_id}/reject`        | Reject a command                    |
| POST   | `/commands/{command_id}/expire`        | Mark a command as expired           |
| POST   | `/commands/{command_id}/lost`          | Mark a command as lost              |

## Communication model

Signal propagation delay is calculated from spacecraft distance using the speed of light.

The mission communication profile can additionally define:

- Network latency
- Packet-loss percentage
- Signal availability

Commands progress through the controlled lifecycle:

```text
CREATED → QUEUED → IN_TRANSIT → DELIVERED → EXECUTED
```

Commands may also terminate as REJECTED, EXPIRED or LOST.

Every command status change is persisted in an append-only audit log.

## Database migration

```bash
alembic upgrade head
```

## Tests

```bash
pytest
```

## Default Port

`8005`
