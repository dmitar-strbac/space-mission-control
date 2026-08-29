import type {
  MissionAlert,
  TelemetryPoint,
} from "../types/telemetry";

import {
  apiRequest,
  getStoredAccessToken,
  getWebSocketBaseUrl,
} from "./apiClient";

export function getRecentTelemetry(
  missionId: string,
  limit = 120,
): Promise<TelemetryPoint[]> {
  return apiRequest<TelemetryPoint[]>(
    `/api/telemetry/telemetry/${missionId}?limit=${limit}`,
  );
}

export function getMissionAlerts(
  missionId: string,
  limit = 100,
): Promise<MissionAlert[]> {
  return apiRequest<MissionAlert[]>(
    `/api/telemetry/missions/${missionId}/alerts?limit=${limit}`,
  );
}

export function getTelemetryWebSocketUrl(
  missionId: string,
): string | null {
  const token = getStoredAccessToken();

  if (!token) {
    return null;
  }

  const url = new URL(
    `/ws/missions/${missionId}/telemetry`,
    getWebSocketBaseUrl(),
  );

  url.searchParams.set("token", token);

  return url.toString();
}
