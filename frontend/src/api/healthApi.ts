import type { ServicesHealthResponse } from "../types/health";
import { apiRequest } from "./apiClient";

export function getServicesHealth(): Promise<ServicesHealthResponse> {
  return apiRequest<ServicesHealthResponse>("/health/services");
}
