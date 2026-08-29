import type {
  Simulation,
  SimulationAdvanceResponse,
  SimulationState,
} from "../types/simulation";

import { apiRequest } from "./apiClient";

export function getSimulation(
  missionId: string,
): Promise<Simulation> {
  return apiRequest<Simulation>(
    `/api/flight-dynamics/simulations/${missionId}`,
  );
}

export function getSimulationState(
  missionId: string,
): Promise<SimulationState> {
  return apiRequest<SimulationState>(
    `/api/flight-dynamics/simulations/${missionId}/state`,
  );
}

export function startSimulation(
  missionId: string,
): Promise<Simulation> {
  return apiRequest<Simulation>(
    `/api/flight-dynamics/simulations/${missionId}/start`,
    {
      method: "POST",
    },
  );
}

export function pauseSimulation(
  missionId: string,
): Promise<Simulation> {
  return apiRequest<Simulation>(
    `/api/flight-dynamics/simulations/${missionId}/pause`,
    {
      method: "POST",
    },
  );
}

export function resumeSimulation(
  missionId: string,
): Promise<Simulation> {
  return apiRequest<Simulation>(
    `/api/flight-dynamics/simulations/${missionId}/resume`,
    {
      method: "POST",
    },
  );
}

export function advanceSimulation(
  missionId: string,
  realDurationSeconds = 1,
): Promise<SimulationAdvanceResponse> {
  return apiRequest<SimulationAdvanceResponse>(
    `/api/flight-dynamics/simulations/${missionId}/advance`,
    {
      method: "POST",
      body: JSON.stringify({
        real_duration_s: realDurationSeconds,
      }),
    },
  );
}
