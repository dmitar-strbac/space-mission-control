# ⚛️ Frontend

## 🎯 Goal

Provide the interactive Mission Control interface for the Space Mission Control platform.

The frontend transforms the distributed backend capabilities into a unified operator experience for creating missions, preparing mission resources, reviewing trajectory plans, authorizing mission execution and monitoring spacecraft operations.

The interface is designed as a modern engineering-oriented Mission Control dashboard while maintaining clear visualization of distributed workflows and orbital mission state.

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

### 🌍 Trajectory Visualization

- Initial and target orbit visualization
- Orbital altitude overview
- Delta-v requirements
- Transfer duration
- Propellant estimation
- Planned maneuver information

### 🚀 Launch Authorization

- Mission launch authorization
- Early launch confirmation for scheduled missions
- Animated launch sequence
- Mission transition from READY to IN_PROGRESS

### 🎛️ Mission Control

- Operator-focused dashboard
- Backend service health overview
- Mission activity overview
- Spacecraft availability monitoring
- Responsive space-themed interface

## 🛠️ Technology Stack

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- TanStack Query
- Lucide React

## 🔌 Backend Integration

The frontend communicates with the platform through the API Gateway rather than accessing individual microservices directly.

The API Gateway provides:

- Authentication
- REST API routing
- Service health aggregation
- WebSocket proxying
- Centralized access to backend services

Real-time mission data is delivered through WebSocket connections for telemetry and operational updates.

## 🏗️ Architecture

The frontend follows a component-based React architecture with dedicated layers for:

- Pages and mission workflows
- Reusable UI components
- API communication
- Authentication state
- Domain types
- Shared formatting and utility functions

Server state is managed through **TanStack Query**, while authentication and application-level state are handled through React context and local component state where appropriate.

## 🎨 Interface Design

The interface uses a space-inspired Mission Control visual language designed for technical clarity rather than purely decorative presentation.

The design includes:

- Dark command-center interface
- Mission and spacecraft status indicators
- Orbital visualization elements
- Workflow progress visualization
- Operational cards and telemetry panels
- Subtle animations and transitions
- Dedicated launch sequence animation

## 🚧 Development Status

Mission management and mission preparation workflows are implemented.

Current and upcoming frontend work focuses on:

- Live mission execution monitoring
- Real-time telemetry visualization
- Mission command interface
- Safety alerts and emergency controls
- Final end-to-end integration and UI polish

## 🌐 Default Port

`5173`
