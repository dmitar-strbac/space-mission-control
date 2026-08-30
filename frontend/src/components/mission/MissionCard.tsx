import {
  CalendarClock,
  ChevronRight,
  Gauge,
  Orbit,
  Users,
} from "lucide-react";
import { Link } from "react-router-dom";

import type { Mission } from "../../types/mission";
import {
  formatDateTime,
  formatLabel,
} from "../../utils/formatters";
import { missionTypeLabels } from "../../utils/mission";
import { MissionStatusBadge } from "./MissionStatusBadge";

interface MissionCardProps {
  mission: Mission;
}

export function MissionCard({
  mission,
}: MissionCardProps) {
  const targetAltitude =
    typeof mission.target_parameters.target_altitude_km ===
    "number"
      ? mission.target_parameters.target_altitude_km
      : null;

  return (
    <Link
      className="mission-card"
      to={`/missions/${mission.id}`}
    >
      <div className="mission-card-header">
        <div className="mission-card-orbit-icon">
          <Orbit size={20} />
        </div>

        <MissionStatusBadge status={mission.status} />
      </div>

      <div className="mission-card-title">
        <span>{missionTypeLabels[mission.mission_type]}</span>
        <h3>{mission.name}</h3>
      </div>

      <div className="mission-card-data">
        <div>
          <Users size={15} />
          <span>
            Crew
            <strong>{mission.crew_count}</strong>
          </span>
        </div>

        <div>
          <Gauge size={15} />
          <span>
            Target
            <strong>
              {targetAltitude !== null
                ? `${targetAltitude} km`
                : formatLabel(mission.target_type)}
            </strong>
          </span>
        </div>

        <div>
          <CalendarClock size={15} />
          <span>
            Launch
            <strong>
              {formatDateTime(
                mission.planned_launch_time,
              )}
            </strong>
          </span>
        </div>
      </div>

      <div className="mission-card-footer">
        <span>
          Simulation {mission.simulation_speed}×
        </span>

        <span className="mission-card-open">
          Open mission
          <ChevronRight size={15} />
        </span>
      </div>
    </Link>
  );
}
