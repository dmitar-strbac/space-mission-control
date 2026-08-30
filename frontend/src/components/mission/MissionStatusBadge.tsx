import type { MissionStatus } from "../../types/mission";
import { missionStatusLabels } from "../../utils/mission";

interface MissionStatusBadgeProps {
  status: MissionStatus;
}

export function MissionStatusBadge({
  status,
}: MissionStatusBadgeProps) {
  const statusClass = status
    .toLowerCase()
    .replaceAll("_", "-");

  return (
    <span
      className={`mission-status-badge status-${statusClass}`}
    >
      <span />
      {missionStatusLabels[status]}
    </span>
  );
}
