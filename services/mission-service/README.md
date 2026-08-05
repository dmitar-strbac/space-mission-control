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

## Tests

```bash
pytest
```

## Default port

`8001`
