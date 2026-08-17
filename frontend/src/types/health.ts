export type ServiceHealthStatus =
  | "healthy"
  | "unhealthy"
  | "degraded"
  | "unknown";

export interface ServiceHealth {
  service: string;
  status: ServiceHealthStatus | string;
  circuit_breaker?: string;
  latency_ms?: number;
  detail?: string;
}

export interface ServicesHealthResponse {
  services: ServiceHealth[];
}
