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
└── README.md
```

**`asyncapi/`**
Reserved for AsyncAPI documentation describing event channels, publishers, consumers, and message payloads.

**`events/`**
Contains shared integration-event schemas. The current event envelope defines metadata common to all asynchronous messages exchanged between services.

**`schemas/`**
Reserved for reusable schema definitions and service-specific event payloads.

---

## ✉️ Event Envelope

Every command or integration event should be wrapped in the shared event envelope, which keeps transport metadata consistent while allowing each event type to define its own payload schema.

| Field            | Description                                                            |
| ---------------- | ---------------------------------------------------------------------- |
| `event_id`       | Unique identifier of the event instance                                |
| `event_type`     | Domain-oriented event name (e.g. `mission.created`)                    |
| `event_version`  | Schema version of this event type                                      |
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

## 🛰️ Planned Event Groups

Service-specific contracts will be introduced together with the corresponding functionality. Expected groups include:

- mission lifecycle events;
- vehicle reservation and validation events;
- trajectory planning events;
- simulation state and maneuver events;
- communication and command events;
- telemetry and safety events;
- Saga commands and compensation events;
- emergency abort events.

---

## ✅ Validation

Schemas should be validated before integration events are published or consumed. Repository-wide checks can be executed with:

```bash
uv run pre-commit run --all-files
```

This ensures that JSON schemas and related contract files remain syntactically valid and consistently formatted.
