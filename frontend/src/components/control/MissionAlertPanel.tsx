import {
  AlertTriangle,
  CheckCircle2,
  RadioTower,
  ShieldAlert,
} from "lucide-react";

import type {
  MissionAlert,
} from "../../types/telemetry";

import {
  formatLabel,
} from "../../utils/formatters";

interface MissionAlertPanelProps {
  alerts: MissionAlert[];
}

function formatAlertTime(
  value: string,
) {
  return new Date(
    value,
  ).toLocaleTimeString(
    [],
    {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    },
  );
}

function severityIcon(
  severity:
    MissionAlert["severity"],
) {
  switch (severity) {
    case "CRITICAL":
      return (
        <ShieldAlert
          size={17}
        />
      );

    case "WARNING":
    case "CAUTION":
      return (
        <AlertTriangle
          size={17}
        />
      );

    default:
      return (
        <RadioTower
          size={17}
        />
      );
  }
}

export function MissionAlertPanel({
  alerts,
}: MissionAlertPanelProps) {
  const activeAlerts =
    alerts.filter(
      (alert) =>
        alert.resolved_at ===
        null,
    );

  return (
    <article className="mission-alert-panel">
      <div className="mission-alert-panel-heading">
        <div>
          <span className="eyebrow">
            Safety Monitoring
          </span>

          <h2>
            Mission alerts
          </h2>
        </div>

        <span
          className={
            activeAlerts.length >
            0
              ? "mission-alert-count active"
              : "mission-alert-count nominal"
          }
        >
          {
            activeAlerts.length
          }{" "}
          ACTIVE
        </span>
      </div>

      {activeAlerts.length ===
      0 ? (
        <div className="mission-alert-empty">
          <CheckCircle2
            size={22}
          />

          <div>
            <strong>
              Safety systems nominal
            </strong>

            <span>
              No unresolved
              mission alerts.
            </span>
          </div>
        </div>
      ) : (
        <div className="mission-alert-list">
          {activeAlerts.map(
            (alert) => (
              <div
                className={
                  `mission-alert-row ` +
                  `mission-alert-${alert.severity.toLowerCase()}`
                }
                key={alert.id}
              >
                <div className="mission-alert-icon">
                  {severityIcon(
                    alert.severity,
                  )}
                </div>

                <div className="mission-alert-content">
                  <div>
                    <strong>
                      {formatLabel(
                        alert.alert_type,
                      )}
                    </strong>

                    <span>
                      {
                        alert.severity
                      }
                    </span>
                  </div>

                  <p>
                    {
                      alert.message
                    }
                  </p>

                  <small>
                    Last detected{" "}
                    {formatAlertTime(
                      alert.last_seen_at,
                    )}
                  </small>
                </div>
              </div>
            ),
          )}
        </div>
      )}
    </article>
  );
}
