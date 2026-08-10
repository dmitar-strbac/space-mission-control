# 🛰️ Flight Dynamics Service

The Flight Dynamics Service is responsible for physically consistent spacecraft state propagation, maneuver execution and simulation-session management.

## Responsibilities

- Create and manage simulation sessions
- Propagate spacecraft state using numerical integration
- Calculate gravitational acceleration using the shared orbital mechanics package
- Execute planned orbital maneuvers
- Update spacecraft velocity and position during simulation
- Calculate propellant consumption and spacecraft mass changes during burns
- Support simulation start, pause and resume operations
- Persist simulation sessions and periodic checkpoints using PostgreSQL and SQLAlchemy
- Manage database schema through Alembic migrations
- Provide unit and integration test coverage

> **Note:** Real-time telemetry streaming, anomaly detection, communication effects and event-driven mission orchestration are implemented separately in later features. NATS integration with mission execution workflows is intentionally outside the scope of this service branch.

## API

| Method | Route                                  | Purpose                              |
| ------ | -------------------------------------- | ------------------------------------ |
| POST   | `/simulations`                         | Create a simulation session          |
| GET    | `/simulations/{mission_id}`            | Get the simulation for a mission     |
| POST   | `/simulations/{mission_id}/start`      | Start a simulation                   |
| POST   | `/simulations/{mission_id}/pause`      | Pause a simulation                   |
| POST   | `/simulations/{mission_id}/resume`     | Resume a simulation                  |
| POST   | `/simulations/{mission_id}/step`       | Advance the simulation               |
| POST   | `/simulations/{mission_id}/maneuvers`  | Execute a planned maneuver           |
| POST   | `/simulations/{mission_id}/checkpoint` | Persist the current simulation state |

## Physical model

The current implementation focuses on the basic LEO scope using a two-dimensional, Earth-centered orbital model.

Flight propagation uses the shared `space-mission-orbital-mechanics` package for:

- Orbital state vectors
- Newtonian gravitational acceleration
- RK4 numerical integration
- Engine thrust acceleration
- Propellant mass flow
- Spacecraft mass updates

Simulation speed controls the relationship between simulated and real time without changing the physical equations used for numerical propagation.

Trajectory generation and maneuver planning are handled by the Trajectory Service.

## Database migration

```bash
alembic upgrade head
```

## Tests

```bash
pytest
```

## Default Port

`8004`
