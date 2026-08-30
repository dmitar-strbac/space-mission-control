# ⚛️ Frontend

## 🎯 Goal

Provide the interactive Mission Control interface for the Space Mission Control platform.

The frontend transforms the distributed backend capabilities into a unified operator experience for creating missions, preparing mission resources, reviewing trajectory plans, authorizing mission execution and monitoring spacecraft operations in real time.

The interface is designed as a modern engineering-oriented Mission Control dashboard while maintaining clear visualization of distributed workflows, orbital state, telemetry and mission safety.

## ✨ Features

### 🚀 Mission Management

- Mission creation workflow
- Mission configuration and spacecraft selection
- Mission lifecycle visualization
- Mission status tracking
- Planned launch configuration
- Mission overview and operational details

### 🛰️ Mission Preparation

- Prepare Mission workflow
- Distributed Saga progress visualization
- Individual preparation step monitoring
- Failure and compensation state visualization
- Spacecraft reservation status
- Trajectory planning results
- Mission readiness indication

### 🌍 Trajectory & Orbital Visualization

- Initial and target orbit visualization
- Planned maneuver visualization
- Live spacecraft position
- Actual mission trajectory tracking
- Orbital altitude overview
- Delta-v requirements
- Transfer duration and propellant estimation
- Earth-centered orbital visualization

### 🚀 Launch Authorization

- Mission launch authorization
- Early launch confirmation for scheduled missions
- Animated launch sequence
- Mission transition from `READY` to `IN_PROGRESS`

### 🎛️ Live Mission Control

- Real-time mission telemetry
- Live orbital state visualization
- Navigation and propulsion monitoring
- Life-support and power monitoring
- Telemetry history charts
- Mission timeline and operational state
- Simulation pause and resume controls
- Safety alert visualization
- Emergency Abort control
- Backend service health overview

## 🛠️ Technology Stack

- React
- TypeScript
- Vite
- React Router
- TanStack Query
- Lucide React
- D3 Geo
- TopoJSON

## 🔌 Backend Integration

The frontend communicates with the platform exclusively through the API Gateway rather than accessing individual microservices directly.

The API Gateway provides:

- Authentication and authorization
- REST API routing
- Service health aggregation
- WebSocket proxying
- Centralized access to backend services

Real-time telemetry is delivered through mission-scoped WebSocket connections proxied by the API Gateway from the Telemetry & Safety Service.

## 🏗️ Architecture

The frontend follows a component-based React architecture with dedicated layers for:

- Pages and mission workflows
- Reusable UI components
- API communication
- Authentication state
- Domain types
- Shared formatting and utility functions

Server state is managed through **TanStack Query**, while authentication and application-level state are handled through React context and local component state where appropriate.

Mission Control combines REST-based mission state with WebSocket telemetry to provide both persistent backend state and continuously updated operational data.

## 🎨 Interface Design

The interface uses a space-inspired Mission Control visual language designed for technical clarity rather than purely decorative presentation.

The design includes:

- Dark command-center interface
- Mission and spacecraft status indicators
- Earth and orbital visualization
- Real-time telemetry panels and charts
- Workflow progress visualization
- Safety and operational controls
- Subtle animations and transitions
- Dedicated launch sequence animation
- Responsive layouts

## 🚧 Development Status

The complete frontend workflow for the current Low Earth Orbit mission model is implemented.

This includes mission creation, distributed preparation, trajectory review, launch authorization, autonomous mission monitoring, real-time telemetry, orbital visualization, mission controls, safety alerts and Emergency Abort handling.

Future frontend work will accompany planned simulation extensions such as LEO rendezvous and lunar missions.

## 🌐 Default Port

`5173`
