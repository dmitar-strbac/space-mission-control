# 📊 Telemetry & Safety Service

The Telemetry & Safety Service is responsible for transforming simulation state into operational telemetry, detecting safety anomalies and streaming mission data to connected clients in real time.

## Responsibilities

- Consume spacecraft state updates from the Flight Dynamics Service
- Derive navigation, propulsion, life-support and power telemetry
- Incorporate communication status from the Communication Service
- Persist telemetry points using MongoDB
- Evaluate deterministic safety thresholds
- Detect resource, communication and trajectory anomalies
- Create and maintain mission alert lifecycle
- Persist alert and anomaly history
- Publish safety recommendations through NATS JetStream
- Stream telemetry and alerts using WebSocket connections
- Provide REST access to recent telemetry and safety history
- Provide unit and integration test coverage

> **Note:** Telemetry values are never randomly generated. Every telemetry value originates from the physical simulation state, the Communication Service, or a deterministic calculation derived from those values. Fault injection and the complete Emergency Abort workflow are implemented separately in the following feature.

## API

| Method | Route                                 | Purpose                          |
| ------ | ------------------------------------- | -------------------------------- |
| GET    | `/telemetry/{mission_id}`             | Get recent mission telemetry     |
| GET    | `/telemetry/{mission_id}/latest`      | Get the latest telemetry point   |
| GET    | `/missions/{mission_id}/alerts`       | Get mission alert history        |
| GET    | `/missions/{mission_id}/anomalies`    | Get detected anomaly history     |
| WS     | `/ws/missions/{mission_id}/telemetry` | Stream live telemetry and alerts |

## Telemetry model

Telemetry is derived from real simulation state published by the Flight Dynamics Service.

The current LEO implementation provides:

- Orbital altitude
- Spacecraft speed
- Vertical speed
- Propellant quantity and percentage
- Current fuel-flow rate
- Remaining delta-v
- Oxygen quantity and percentage
- Estimated remaining oxygen duration
- Battery energy and percentage
- Estimated remaining power duration
- Communication signal status
- One-way communication delay
- Packet-loss percentage

Fields that depend on rendezvous or lunar mission functionality remain optional until those mission scopes are implemented.

## Safety model

Safety monitoring uses deterministic and configurable thresholds rather than random anomaly generation.

The current implementation detects:

- Low propellant
- Propellant reserve violation
- Low and critical oxygen
- Low power
- Trajectory deviation when deviation data is available
- Degraded communication
- Lost communication

Alerts use the following severity levels:

```text
INFO
CAUTION
WARNING
CRITICAL
```

Persistent alert conditions update an existing active alert instead of creating duplicate alerts for every telemetry sample.

When the underlying condition disappears, the active alert is automatically resolved.

Safety evaluation may publish:

```text
safety.corrective_maneuver.recommended
safety.return.recommended
safety.abort.recommended
```

The Telemetry & Safety Service only recommends safety actions. Mission lifecycle changes and the complete Emergency Abort workflow remain responsibilities of their respective services.

## Event-driven communication

High-frequency state and telemetry events use Core NATS pub/sub:

```text
simulation.state.updated
telemetry.processed
```

Safety-relevant and durable integration events use NATS JetStream:

```text
communication.status.updated
telemetry.alert.created
safety.corrective_maneuver.recommended
safety.return.recommended
safety.abort.recommended
```

This separation prevents high-frequency telemetry samples from unnecessarily filling the durable workflow stream while preserving reliable delivery for important safety events.

## Database

MongoDB is used because telemetry and anomaly data are naturally document-oriented and time-series-like.

The service owns the following collections:

```text
telemetry_points
alerts
anomaly_events
```

Telemetry points are indexed by mission and recording time to support efficient retrieval of the most recent mission history.

## Real-time streaming

The service exposes a mission-scoped WebSocket endpoint:

```text
/ws/missions/{mission_id}/telemetry
```

Connected clients receive:

- Processed telemetry updates
- Newly created or escalated safety alerts

The frontend is therefore isolated from internal numerical simulation steps and consumes only controlled telemetry updates.

## Tests

```bash
pytest
```

## Default port

`8006`
