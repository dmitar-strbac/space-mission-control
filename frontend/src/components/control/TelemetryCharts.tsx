import type {
  TelemetryPoint,
} from "../../types/telemetry";

import {
  TelemetryChart,
} from "./TelemetryChart";

interface TelemetryChartsProps {
  telemetry: TelemetryPoint[];
}

export function TelemetryCharts({
  telemetry,
}: TelemetryChartsProps) {
  return (
    <section className="telemetry-charts-grid">
      <TelemetryChart
        title="Orbital Altitude"
        subtitle="Navigation"
        unit="km"
        series={[
          {
            label: "Altitude",
            values:
              telemetry.map(
                (point) =>
                  point.navigation
                    .altitude_km,
              ),
            variant: "primary",
          },
        ]}
      />

      <TelemetryChart
        title="Velocity & Deviation"
        subtitle="Flight Dynamics"
        unit="km/s · km"
        series={[
          {
            label: "Velocity",
            values:
              telemetry.map(
                (point) =>
                  point.navigation
                    .speed_km_s,
              ),
            variant: "primary",
          },
          {
            label: "Deviation",
            values:
              telemetry.map(
                (point) =>
                  point.navigation
                    .trajectory_deviation_km,
              ),
            variant: "caution",
          },
        ]}
      />

      <TelemetryChart
        title="Resource Reserves"
        subtitle="Spacecraft Systems"
        unit="%"
        series={[
          {
            label: "Propellant",
            values:
              telemetry.map(
                (point) =>
                  point.propulsion
                    .propellant_percent,
              ),
            variant: "primary",
          },
          {
            label: "Oxygen",
            values:
              telemetry.map(
                (point) =>
                  point.life_support
                    .oxygen_percent,
              ),
            variant: "success",
          },
          {
            label: "Power",
            values:
              telemetry.map(
                (point) =>
                  point.power
                    .battery_percent,
              ),
            variant: "caution",
          },
        ]}
      />

      <TelemetryChart
        title="Signal Delay"
        subtitle="Communications"
        unit="ms"
        series={[
          {
            label: "One-way delay",
            values:
              telemetry.map(
                (point) =>
                  point.communication
                    ?.one_way_delay_ms ??
                  null,
              ),
            variant: "secondary",
          },
        ]}
      />
    </section>
  );
}
