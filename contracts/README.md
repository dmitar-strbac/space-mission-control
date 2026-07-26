# Event Contracts

This directory contains versioned schemas for commands and integration events exchanged between Space Mission Control services.

## Structure

```text
contracts/
└── events/
    └── event-envelope.schema.json
```

The event envelope defines the common metadata shared by all asynchronous events.

Service-specific commands and events will be introduced together with the corresponding business functionality.
