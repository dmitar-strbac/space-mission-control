# 🚀 Space Mission Control

**A distributed microservice platform for planning, preparing, and simulating orbital space missions in the Earth–Moon system.**

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Vite-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![NATS](https://img.shields.io/badge/NATS-JetStream-27AAE1?logo=natsdotio&logoColor=white)](https://nats.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](./LICENSE)

---

## 🌌 Overview

The platform combines orbital mechanics, spacecraft resource management,
trajectory planning, distributed workflows and real-time telemetry into a
physically consistent simulation built around modern backend architecture.

The project is designed around a **physically consistent simulation model**, where every maneuver influences the spacecraft state according to simplified orbital physics rather than scripted behavior.

Originally developed as a **Bachelor's Thesis** at the **Faculty of Technical Sciences, University of Novi Sad**, the project is also intended to serve as a long-term portfolio project demonstrating modern backend architecture and distributed systems design.

---

## 🎯 Why this project

The goal of this project is not to reproduce a complete aerospace engineering simulator.

Instead, it explores how modern distributed backend systems can be combined with a simplified but physically consistent orbital simulation to model complex mission planning and execution workflows.

The project emphasizes software architecture, clear service boundaries, event-driven communication, distributed transactions and deterministic simulation rather than graphical realism or aerospace-level engineering accuracy.

By combining concepts from orbital mechanics with modern microservice architecture, the project demonstrates how engineering principles and distributed software systems can be integrated into a cohesive simulation platform.

---

## 📸 Preview

Application screenshots, architecture diagrams and demonstration GIFs will be added as development progresses.

---

## ✨ Features

- 🚀 Mission planning and preparation
- 🛰️ Orbital flight simulation
- 🌍 Physically consistent orbital mechanics
- 📡 Real-time telemetry streaming
- ⚙️ Distributed microservice architecture
- 🔄 Event-driven communication using NATS JetStream
- 📈 Live WebSocket updates
- 🛡️ Fault injection and emergency scenarios
- 📐 Numerical orbit propagation
- 🧮 Delta-v and propellant calculations
- ⚖️ Database-per-service architecture
- 🔥 Distributed mission preparation using Saga orchestration
- 🐳 Fully containerized development environment

---

## 🏗️ System Architecture

The platform is organized as a distributed microservice system.

| Service                    | Responsibility                                       |
| -------------------------- | ---------------------------------------------------- |
| API Gateway                | Authentication, routing, health checks               |
| Mission Service            | Mission lifecycle and Saga orchestration             |
| Vehicle Service            | Spacecraft configuration and resource validation     |
| Trajectory Service         | Orbital planning and maneuver generation             |
| Flight Dynamics Service    | Orbital mechanics simulation                         |
| Communication Service      | Signal delay and command delivery                    |
| Telemetry & Safety Service | Telemetry processing, alerts and WebSocket streaming |

> 📌 Architecture diagram will be added as development progresses.

---

## 🛠️ Technology Stack

### 🐍 Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PyMongo

### ⚛️ Frontend

- React
- TypeScript
- Vite

### 🗄️ Databases

- PostgreSQL
- MongoDB

### 🧪 Testing

- pytest
- mypy
- ruff
- pre-commit

### 🧮 Scientific Computing

- NumPy
- SciPy

### 📡 Messaging

- NATS
- NATS JetStream

### 🐳 Infrastructure

- Docker
- Docker Compose

---

## 🌍 Physical Simulation

Unlike most educational projects, Space Mission Control is based on a simplified but physically consistent orbital mechanics model.

The simulation includes:

- Newtonian gravity
- Orbital state vectors
- Spacecraft mass variation
- Propellant consumption
- Delta-v estimation
- Orbital maneuver execution
- Numerical integration (RK4 / `solve_ivp`)
- Circular orbit validation using real reference values

The initial implementation focuses on **Low Earth Orbit (LEO)** missions while providing an extensible architecture for rendezvous and future lunar missions.

---

## 📂 Repository Structure

```text
space-mission-control/
│
├── services/
│   ├── api-gateway/
│   ├── mission-service/
│   ├── vehicle-service/
│   ├── trajectory-service/
│   ├── flight-dynamics-service/
│   ├── communication-service/
│   └── telemetry-safety-service/
│
├── frontend/
├── contracts/
├── infrastructure/
├── docs/
├── scripts/
└── packages/
    ├── orbital-mechanics/
    └── messaging/
```

---

## 🚀 Getting Started

### Prerequisites

- Docker
- Docker Compose

### Clone the repository

```bash
git clone https://github.com/dmitar-strbac/space-mission-control.git
cd space-mission-control
```

### Configure environment

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### Start the development environment

```bash
docker compose up --build
```

---

## 🗺️ Roadmap

The project has completed the **Core Mission Simulation**, **Distributed Mission Preparation**, and **Telemetry & Mission Safety** backend milestones, providing the main domain services required for planning, preparing, simulating and safely aborting Low Earth Orbit (LEO) missions.

The roadmap below outlines the remaining gateway, frontend and final integration work.

- [x] Project architecture
- [x] Repository initialization
- [x] Infrastructure setup
- [x] Mission Service
- [x] Vehicle Service
- [x] Trajectory Service
- [x] Flight Dynamics Service
- [x] Telemetry & Safety Service
- [x] Communication Service
- [x] API Gateway
- [ ] React frontend
- [x] Prepare Mission Saga
- [x] Real-time telemetry
- [x] Emergency Abort workflow
- [ ] Docker deployment

---

## 🔭 Project Scope

- Low Earth Orbit missions
- Orbital maneuver planning
- Trajectory validation
- Delta-v calculations
- Propellant consumption
- Oxygen and power management
- Communication latency simulation
- Mission timeline
- Real-time telemetry visualization
- Trajectory deviation detection
- Distributed Saga transactions
- Fault injection scenarios
- Emergency Abort procedures

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Dmitar Štrbac**

Bachelor's Thesis Project

Faculty of Technical Sciences

University of Novi Sad
