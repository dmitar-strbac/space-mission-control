# 🛰️ Orbital Mechanics

Reusable physical simulation library for the **Space Mission Control** platform.

The package provides deterministic orbital-mechanics calculations shared by the trajectory-planning and flight-dynamics domains. It is intentionally isolated from FastAPI, databases, NATS, and service lifecycle concerns, keeping the physical model independent and easy to test in isolation.

---

## 🎯 Purpose

The library represents the physical foundation of the mission simulation system. It is responsible for:

- modelling spacecraft position, velocity, mass, and propellant;
- calculating Earth gravity;
- creating initial circular low Earth orbit states;
- calculating orbital velocity and period;
- estimating available delta-v;
- modelling engine thrust and propellant consumption;
- propagating spacecraft state using fourth-order Runge-Kutta integration.

---

## 📦 Model Scope

The current implementation supports the core thesis scope:

- two-dimensional motion in a single orbital plane;
- Earth-centred coordinate system;
- point-mass Earth gravity;
- initial circular low Earth orbit states;
- spacecraft position and velocity state vectors;
- total mass and remaining propellant;
- engine thrust and specific impulse;
- propellant mass flow;
- ideal available delta-v using the Tsiolkovsky rocket equation;
- fourth-order Runge-Kutta state propagation.

---

## 📐 Units

All internal calculations use coherent SI units.

| Quantity              | Unit                     |
| --------------------- | ------------------------ |
| Position and distance | metre                    |
| Time                  | second                   |
| Velocity              | metre per second         |
| Acceleration          | metre per second squared |
| Mass                  | kilogram                 |
| Force                 | newton                   |
| Specific impulse      | second                   |

Conversions to kilometres, kilometres per second, and minutes are performed **only** at API or presentation boundaries. This prevents accidental mixing of internal simulation units with values displayed to the user.

---

## 🧭 State Vector

The two-dimensional spacecraft state contains:

```text
position           = [x, y]
velocity           = [vx, vy]
total_mass_kg
propellant_mass_kg
elapsed_time_s
```

State objects are **immutable** — every integration step produces a new state instead of modifying the previous one.

---

## 🌍 Gravity Model

Earth gravity is calculated using:

```text
a = -μ · r / |r|³
```

where:

- `a` — gravitational acceleration
- `r` — spacecraft position vector
- `μ` — Earth's standard gravitational parameter

Earth is currently modelled as a point mass located at the coordinate-system origin.

---

## 🚀 Propulsion Model

Available delta-v is calculated using the **Tsiolkovsky rocket equation**:

```text
Δv = Isp · g₀ · ln(m₀ / mf)
```

Propellant mass flow is derived from engine thrust and specific impulse:

```text
mass_flow = thrust / (Isp · g₀)
```

During active engine operation:

- propellant mass decreases;
- total spacecraft mass decreases by the same amount;
- dry spacecraft mass remains unchanged;
- thrust acceleration depends on the current total mass.

---

## 🔢 Numerical Integration

Spacecraft state is propagated using a **fourth-order Runge-Kutta (RK4)** integrator. The integrator updates:

- position;
- velocity;
- total mass;
- remaining propellant;
- elapsed simulation time.

Simulation-speed factors are intentionally excluded from the physical model — they belong to the service layer and control the relationship between simulation time and wall-clock time, without affecting numerical accuracy.

---

## ✅ Verification

The test suite verifies the model against known low Earth orbit reference values:

- circular velocity at ~400 km: **7.66–7.80 km/s**;
- circular orbital period at ~400 km: **92–93 minutes**;
- stable propagation over one complete circular orbit;
- approximate conservation of specific orbital energy;
- consistent total-mass and propellant consumption;
- correct direction and magnitude of gravitational acceleration.

---

## 🧪 Running Tests

From the repository root:

```bash
uv run --package space-mission-orbital-mechanics pytest
```

Static checks:

```bash
uv run ruff check packages/orbital-mechanics
uv run ruff format packages/orbital-mechanics --check
uv run mypy packages/orbital-mechanics/src
```

---

## ⚠️ Current Limitations

The current physical core intentionally excludes:

- atmospheric drag;
- Earth rotation;
- three-dimensional orbital motion;
- orbital plane changes and inclination;
- Moon gravity;
- n-body dynamics;
- relativistic effects;
- detailed launch physics;
- atmospheric-entry simulation;
- structural and thermodynamic spacecraft models.
