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

## Fault Injection

Active simulation faults modify the real runtime state used by the physical simulation.

Supported basic-scope faults include:

- engine thrust loss;
- propellant leak;
- oxygen leak;
- electrical power failure;
- targeting error.

Fault effects are applied directly during simulation propagation. Telemetry and safety alerts therefore observe the resulting physical or resource changes rather than synthetic fault values.

## Emergency Abort Execution

When an Emergency Abort command reaches the spacecraft simulation, Flight Dynamics:

1. cancels pending and active nominal maneuvers;
2. exposes the current physical state for emergency trajectory planning;
3. receives the validated `DEORBIT_BURN`;
4. verifies remaining propellant and engine availability;
5. executes the maneuver using the normal propulsion and mass-consumption model;
6. creates a final checkpoint;
7. publishes `simulation.abort.completed`.

If the maneuver cannot be physically executed, the service publishes an abort failure instead of forcing the mission into a successful state.

## Tests

```bash
pytest
```

## Default Port

`8004`
