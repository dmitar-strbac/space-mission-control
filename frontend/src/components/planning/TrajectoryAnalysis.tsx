import {
  ArrowUpRight,
  Clock3,
  Fuel,
  Gauge,
  Orbit,
  ShieldCheck,
} from "lucide-react";

import type {
  Maneuver,
  TrajectoryPlan,
} from "../../types/trajectory";
import {
  formatDateTime,
  formatLabel,
  formatNumber,
} from "../../utils/formatters";
import { OrbitPlanPreview } from "./OrbitPlanPreview";

interface TrajectoryAnalysisProps {
  trajectory: TrajectoryPlan;
  maneuvers: Maneuver[];
  targetAltitudeKm: number;
}

export function TrajectoryAnalysis({
  trajectory,
  maneuvers,
  targetAltitudeKm,
}: TrajectoryAnalysisProps) {
  return (
    <section className="trajectory-analysis">
      <div className="trajectory-analysis-heading">
        <div>
          <span className="eyebrow">
            Trajectory Solution
          </span>

          <h2>Nominal flight plan</h2>

          <p>
            Trajectory Service generated and validated
            the orbital transfer required for this
            mission.
          </p>
        </div>

        <div className="trajectory-feasible-badge">
          <ShieldCheck size={15} />
          {trajectory.status}
        </div>
      </div>

      <div className="trajectory-analysis-layout">
        <OrbitPlanPreview
          targetAltitudeKm={targetAltitudeKm}
        />

        <div className="trajectory-metrics">
          <TrajectoryMetric
            icon={<Orbit size={17} />}
            label="Required Δv"
            value={`${formatNumber(
              trajectory.required_delta_v_m_s,
            )} m/s`}
          />

          <TrajectoryMetric
            icon={<Fuel size={17} />}
            label="Propellant"
            value={`${formatNumber(
              trajectory.estimated_propellant_kg,
            )} kg`}
          />

          <TrajectoryMetric
            icon={<Gauge size={17} />}
            label="Fuel Reserve"
            value={`${formatNumber(
              trajectory.propellant_reserve_percent,
            )}%`}
          />

          <TrajectoryMetric
            icon={<ShieldCheck size={17} />}
            label="Safety Margin"
            value={`${formatNumber(
              trajectory.safety_margin_percent,
            )}%`}
          />

          <div className="trajectory-score-card">
            <div>
              <span>WINDOW SCORE</span>
              <strong>
                {trajectory.window_score}
                <small>/100</small>
              </strong>
            </div>

            <div className="trajectory-score-bar">
              <span
                style={{
                  width: `${trajectory.window_score}%`,
                }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="trajectory-timing-strip">
        <div>
          <Clock3 size={16} />

          <span>
            <small>DEPARTURE</small>
            <strong>
              {formatDateTime(
                trajectory.departure_time,
              )}
            </strong>
          </span>
        </div>

        <ArrowUpRight size={18} />

        <div>
          <Clock3 size={16} />

          <span>
            <small>ESTIMATED ARRIVAL</small>
            <strong>
              {formatDateTime(
                trajectory.arrival_time,
              )}
            </strong>
          </span>
        </div>
      </div>

      <div className="maneuver-sequence">
        <div className="maneuver-sequence-heading">
          <div>
            <span className="eyebrow">
              Maneuver Sequence
            </span>
            <h3>Planned burns</h3>
          </div>

          <span>
            {maneuvers.length} maneuver
            {maneuvers.length === 1 ? "" : "s"}
          </span>
        </div>

        {maneuvers.map((maneuver) => (
          <div
            className="maneuver-row"
            key={maneuver.id}
          >
            <span className="maneuver-sequence-number">
              {String(maneuver.sequence).padStart(
                2,
                "0",
              )}
            </span>

            <div>
              <strong>
                {formatLabel(
                  maneuver.maneuver_type,
                )}
              </strong>

              <span>
                Planned T+
                {formatNumber(
                  maneuver.planned_offset_s,
                  0,
                )}
                s
              </span>
            </div>

            <strong className="maneuver-delta-v">
              {formatNumber(
                maneuver.delta_v_m_s,
              )}{" "}
              m/s
            </strong>

            <span className="maneuver-status">
              {maneuver.status}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}

interface TrajectoryMetricProps {
  icon: React.ReactNode;
  label: string;
  value: string;
}

function TrajectoryMetric({
  icon,
  label,
  value,
}: TrajectoryMetricProps) {
  return (
    <article className="trajectory-metric">
      <div>{icon}</div>

      <span>
        <small>{label}</small>
        <strong>{value}</strong>
      </span>
    </article>
  );
}
