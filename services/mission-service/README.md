# 🚀 Mission Service

The Mission Service is responsible for mission definitions, lifecycle management and maintaining the append-only mission timeline.

## Responsibilities

- Create and manage mission definitions
- Control mission lifecycle transitions
- Maintain the append-only mission timeline
- Persist mission data using PostgreSQL and SQLAlchemy
- Manage database schema through Alembic migrations
- Provide unit and integration test coverage

> **Note:** Prepare Mission Saga orchestration and NATS event publishing are implemented separately as part of the dedicated `prepare-mission-saga` feature.

## API

| Method | Route                     | Purpose                            |
| ------ | ------------------------- | ---------------------------------- |
| POST   | `/missions`               | Create a draft mission             |
| GET    | `/missions`               | List missions                      |
| GET    | `/missions/{id}`          | Get a mission                      |
| POST   | `/missions/{id}/prepare`  | Begin preparation                  |
| POST   | `/missions/{id}/launch`   | Launch a ready mission             |
| POST   | `/missions/{id}/abort`    | Request abort of an active mission |
| GET    | `/missions/{id}/timeline` | Read mission events                |

## Database migration

```bash
alembic upgrade head
```

## Emergency Abort

The Mission Service coordinates the Emergency Abort lifecycle without directly executing physical abort operations.

An abort can originate from:

- an operator request through `POST /missions/{mission_id}/abort`;
- a `safety.abort.recommended` event produced by the Telemetry & Safety Service.

The mission transitions to `ABORTING` before the distributed workflow begins.

```text
IN_PROGRESS
    ↓
ABORTING
    ↓
ABORTED | FAILED
```

The Mission Service publishes `mission.abort.requested` and waits for the participating services to complete the physical abort workflow.

A successful `simulation.abort.completed` event transitions the mission to `ABORTED`. An `abort.failed` event transitions an active abort workflow to `FAILED` with the reported failure reason.

## Tests

```bash
pytest
```

## Default port

`8001`
