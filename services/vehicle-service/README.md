# 🛰️ Vehicle Service

The Vehicle Service is responsible for spacecraft configuration, availability management and preliminary mission-readiness validation.

## Responsibilities

- Create and manage spacecraft configurations
- Maintain spacecraft availability status
- Validate crew and payload capacity
- Validate supported mission types
- Validate maximum mission duration
- Calculate fully fueled spacecraft mass
- Estimate available delta-v using the shared orbital mechanics package
- Persist spacecraft data using PostgreSQL and SQLAlchemy
- Manage database schema through Alembic migrations

> **Note:** Mission reservation, final resource validation and NATS event handling are implemented separately as part of the Prepare Mission Saga.

## API

| Method | Route                       | Purpose                            |
| ------ | --------------------------- | ---------------------------------- |
| POST   | `/spacecraft`               | Create a spacecraft                |
| GET    | `/spacecraft`               | List spacecraft                    |
| GET    | `/spacecraft/{id}`          | Get a spacecraft                   |
| PUT    | `/spacecraft/{id}`          | Update a spacecraft                |
| DELETE | `/spacecraft/{id}`          | Delete a spacecraft                |
| POST   | `/spacecraft/{id}/validate` | Run preliminary mission validation |

## Database migration

```bash
alembic upgrade head
```

## Tests

```bash
pytest
```

## Default Port

`8002`
