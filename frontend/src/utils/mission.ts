import type {
  Mission,
  MissionStatus,
  MissionType,
} from "../types/mission";

export const missionTypeLabels: Record<MissionType, string> = {
  LEO: "Low Earth Orbit",
  LEO_RENDEZVOUS: "LEO Rendezvous",
  LUNAR: "Lunar Mission",
};

export const missionStatusLabels: Record<MissionStatus, string> = {
  DRAFT: "Draft",
  PLANNING: "Planning",
  PREPARING: "Preparing",
  READY: "Ready",
  IN_PROGRESS: "In Progress",
  COMPLETED: "Completed",
  ABORTING: "Aborting",
  ABORTED: "Aborted",
  FAILED_PREPARATION: "Preparation Failed",
  FAILED: "Failed",
};

export function countMissionsByStatus(
  missions: Mission[],
  status: MissionStatus,
): number {
  return missions.filter(
    (mission) => mission.status === status,
  ).length;
}
