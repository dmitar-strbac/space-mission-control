import type { ReactNode } from "react";

interface TelemetryMetricProps {
  icon: ReactNode;
  label: string;
  value: string;
  detail: string;
  progress?: number;

  tone?:
    | "nominal"
    | "caution"
    | "critical";
}

export function TelemetryMetric({
  icon,
  label,
  value,
  detail,
  progress,
  tone = "nominal",
}: TelemetryMetricProps) {
  const normalizedProgress =
    progress === undefined
      ? undefined
      : Math.max(
          0,
          Math.min(100, progress),
        );

  return (
    <article
      className={`telemetry-metric telemetry-tone-${tone}`}
    >
      <div className="telemetry-metric-heading">
        <span className="telemetry-metric-icon">
          {icon}
        </span>

        <span>{label}</span>
      </div>

      <strong>{value}</strong>

      <small>{detail}</small>

      {normalizedProgress !== undefined && (
        <div
          className="telemetry-meter"
          aria-hidden="true"
        >
          <span
            style={{
              width: `${normalizedProgress}%`,
            }}
          />
        </div>
      )}
    </article>
  );
}
