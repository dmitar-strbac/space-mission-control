export type ServiceHealthStatus =
  | "healthy"
  | "unavailable";

export interface ServiceHealth {
  status: ServiceHealthStatus;
  circuit_state: string;
}

export interface ServicesHealthResponse {
  status: "healthy" | "degraded";
  services: Record<string, ServiceHealth>;
}
