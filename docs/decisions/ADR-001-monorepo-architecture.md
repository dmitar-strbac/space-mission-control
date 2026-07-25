# 📄 ADR-001: Monorepo Architecture

## Status

✅ Accepted

---

## Context

Space Mission Control consists of multiple backend microservices, an API Gateway, a React frontend, shared communication contracts and infrastructure configuration.

All components are developed as part of a single Bachelor's Thesis project while remaining independently deployable and maintainable.

---

## Decision

The project adopts a **monorepo architecture**, where all backend services, frontend application, infrastructure configuration and shared documentation are maintained within a single Git repository.

Each microservice remains logically independent with its own source code, configuration, documentation and container image.

---

## Benefits

- Simplified local development
- Centralized documentation
- Easier management of shared event contracts
- Consistent project structure
- Single repository for portfolio presentation and thesis delivery

---

## Trade-offs

- Repository size grows as the project evolves
- Cross-service changes may require coordinated updates
- CI/CD pipelines may become more complex as additional services are introduced
