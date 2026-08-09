# 🌍 Trajectory Service

The Trajectory Service is responsible for planning physically consistent Low Earth Orbit trajectories, generating orbital maneuvers and evaluating trajectory feasibility.

## Responsibilities

- Plan two-dimensional Low Earth Orbit transfers
- Generate orbit-raise and orbit-lower maneuver sequences
- Calculate required delta-v using the shared orbital mechanics package
- Estimate propellant requirements using the rocket equation
- Evaluate trajectory feasibility against available propellant and safety reserves
- Calculate deterministic launch-window suitability scores for basic LEO missions
- Persist trajectory plans, maneuvers and launch-window data using PostgreSQL and SQLAlchemy
- Manage database schema through Alembic migrations
- Provide unit and integration test coverage

> **Note:** Event-driven trajectory planning, automatic recalculation, corrective maneuvers, rendezvous planning and lunar trajectories are implemented separately in later features. NATS integration with the Prepare Mission Saga is intentionally outside the scope of this service branch.

## API

| Method | Route                                  | Purpose                               |
| ------ | -------------------------------------- | ------------------------------------- |
| POST   | `/trajectories/plan`                   | Create and evaluate a trajectory plan |
| GET    | `/trajectories/{mission_id}`           | Get the latest trajectory plan        |
| GET    | `/trajectories/{mission_id}/maneuvers` | Get maneuvers for the latest plan     |

## Physical model

The current implementation focuses on the basic LEO scope using a two-dimensional, Earth-centered model.

Trajectory calculations use the shared `space-mission-orbital-mechanics` package for:

- Circular-orbit calculations
- Hohmann transfers
- Delta-v estimation
- Propellant estimation
- Orbital state-vector generation

Numerical propagation and actual maneuver execution are handled by the Flight Dynamics Service.

## Database migration

```bash
alembic upgrade head
```

## Tests

```bash
pytest
```

## Default Port

`8003`
