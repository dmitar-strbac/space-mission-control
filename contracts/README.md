# 📜 Event Contracts

Shared, versioned contracts for asynchronous communication between **Space Mission Control** services.

This directory contains JSON schemas for commands and integration events exchanged through NATS and NATS JetStream.

---

## 🎯 Purpose

Event contracts provide a stable communication boundary between independently developed microservices. They ensure that every published event follows a predictable structure and contains the metadata required for:

- event identification;
- correlation across distributed workflows;
- idempotent event processing;
- tracing and logging;
- schema versioning;
- reliable retries and dead-letter handling.

---

## 📁 Structure

```text
contracts/
├── asyncapi/
├── events/
│   └── event-envelope.schema.json
├── schemas/
│   ├── saga/
│   └── telemetry/
└── README.md
```

**`asyncapi/`**
Reserved for AsyncAPI documentation describing event channels, publishers, consumers, and message payloads.

**`events/`**
Contains shared event schemas. The event envelope defines metadata common to all asynchronous messages exchanged between services.

**`schemas/saga/`**
Contains payload schemas used by the distributed Prepare Mission Saga, including reservation, trajectory planning, resource validation, communication profile and simulation initialization events.

**`schemas/telemetry/`**
Contains payload schemas used by the real-time telemetry and mission safety flow, including simulation state updates, communication status updates, processed telemetry, alerts and safety recommendations.

---

## ✉️ Event Envelope

Every command or integration event should be wrapped in the shared event envelope, which keeps transport metadata consistent while allowing each event type to define its own payload schema.

| Field            | Description                                                            |
| ---------------- | ---------------------------------------------------------------------- |
| `event_id`       | Unique identifier of the event instance                                |
| `event_type`     | Domain-oriented event name (e.g. `mission.created`)                    |
| `schema_version` | Schema version of this event type                                      |
| `occurred_at`    | Timestamp when the event was produced                                  |
| `source`         | Originating service                                                    |
| `correlation_id` | Identifier linking events belonging to the same workflow (e.g. a Saga) |
| `causation_id`   | Identifier of the event that directly caused this one                  |
| `payload`        | Event-specific data                                                    |

---

## 🔄 Contract Evolution

Event contracts should evolve in a **backward-compatible** way whenever possible:

- add new optional fields instead of removing existing fields;
- avoid changing the meaning of an existing field;
- introduce a new event version for breaking changes;
- keep event names stable and domain-oriented;
- update producers and consumers together when compatibility cannot be preserved.

---

## 🛰️ Event Groups

The currently implemented contracts are organized around the main asynchronous workflows of the platform.

### Prepare Mission Saga

The Saga contracts cover the distributed mission preparation workflow:

- vehicle reservation and release;
- trajectory planning and cancellation;
- final resource validation;
- communication profile creation and removal;
- simulation initialization and cleanup;
- Saga context and rejected-step information.

These events are delivered through NATS JetStream because they represent durable workflow state and require reliable processing.

### Telemetry and Safety

The telemetry contracts cover the real-time mission monitoring flow:

- `simulation.state.updated`;
- `communication.status.updated`;
- `telemetry.processed`;
- `telemetry.alert.created`;
- `safety.corrective_maneuver.recommended`;
- `safety.return.recommended`;
- `safety.abort.recommended`.

High-frequency simulation state and processed telemetry use Core NATS pub/sub, while safety-relevant integration events use NATS JetStream.

### Planned contracts

Additional contracts will be introduced together with the corresponding functionality, including:

- mission lifecycle events;
- maneuver execution events;
- corrective trajectory workflows;
- fault injection events;
- Emergency Abort workflow events.

---

## ✅ Validation

Schemas should be validated before integration events are published or consumed. Repository-wide checks can be executed with:

```bash
uv run pre-commit run --all-files
```

This ensures that JSON schemas and related contract files remain syntactically valid and consistently formatted.
