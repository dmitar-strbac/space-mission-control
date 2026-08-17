import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  CircleCheck,
  Orbit,
  Rocket,
  Satellite,
  ShieldCheck,
} from "lucide-react";
import { motion } from "motion/react";

import { getServicesHealth } from "../api/healthApi";
import { useAuth } from "../hooks/useAuth";

const serviceDisplayNames: Record<string, string> = {
  "mission-service": "Mission",
  "vehicle-service": "Vehicle",
  "trajectory-service": "Trajectory",
  "flight-dynamics-service": "Flight Dynamics",
  "communication-service": "Communication",
  "telemetry-safety-service": "Telemetry & Safety",
};

export function DashboardPage() {
  const { user } = useAuth();

  const {
    data: healthData,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["services-health"],
    queryFn: getServicesHealth,
    refetchInterval: 15_000,
  });

  const services = healthData?.services ?? [];

  const healthyServices = services.filter(
    (service) =>
      service.status.toLowerCase() === "healthy" ||
      service.status.toLowerCase() === "online",
  ).length;

  return (
    <div className="dashboard-page">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Mission Operations</span>

          <h1>
            Welcome back, {user?.username ?? "operator"}.
          </h1>

          <p>
            Monitor platform readiness and manage orbital mission
            operations from a single control surface.
          </p>
        </div>

        <div className="nominal-badge">
          <span className="system-status-dot" />
          System nominal
        </div>
      </section>

      <section className="stat-grid">
        <DashboardStat
          label="Total Missions"
          value="—"
          description="Mission registry"
          icon={<Rocket size={20} />}
          index={0}
        />

        <DashboardStat
          label="Preparing"
          value="—"
          description="Saga workflows"
          icon={<Orbit size={20} />}
          index={1}
        />

        <DashboardStat
          label="Ready"
          value="—"
          description="Cleared for launch"
          icon={<CircleCheck size={20} />}
          index={2}
        />

        <DashboardStat
          label="Active"
          value="—"
          description="In simulation"
          icon={<Activity size={20} />}
          index={3}
        />
      </section>

      <section className="dashboard-grid">
        <div className="dashboard-card dashboard-card-large">
          <div className="card-heading">
            <div>
              <span className="eyebrow">Mission Activity</span>
              <h2>Recent missions</h2>
            </div>

            <Satellite size={20} />
          </div>

          <div className="dashboard-empty-state">
            <Orbit size={34} />

            <strong>Mission registry awaiting connection</strong>

            <p>
              Mission activity will appear here after the mission API
              is connected in the next implementation step.
            </p>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-heading">
            <div>
              <span className="eyebrow">Distributed System</span>
              <h2>Service network</h2>
            </div>

            <ShieldCheck size={20} />
          </div>

          <div className="service-network-summary">
            <span>
              {isLoading
                ? "Checking services..."
                : isError
                  ? "Gateway unavailable"
                  : `${healthyServices}/${services.length} services operational`}
            </span>
          </div>

          <div className="service-list">
            {isLoading &&
              Array.from({
                length: 6,
              }).map((_, index) => (
                <div
                  className="service-row service-row-loading"
                  key={index}
                />
              ))}

            {!isLoading &&
              services.map((service) => {
                const normalizedStatus =
                  service.status.toLowerCase();

                const healthy =
                  normalizedStatus === "healthy" ||
                  normalizedStatus === "online";

                return (
                  <div className="service-row" key={service.service}>
                    <div className="service-identity">
                      <span
                        className={
                          healthy
                            ? "service-dot healthy"
                            : "service-dot unhealthy"
                        }
                      />

                      <div>
                        <strong>
                          {serviceDisplayNames[service.service] ??
                            service.service}
                        </strong>

                        <span>{service.service}</span>
                      </div>
                    </div>

                    <span
                      className={
                        healthy
                          ? "service-status healthy"
                          : "service-status unhealthy"
                      }
                    >
                      {service.status.toUpperCase()}
                    </span>
                  </div>
                );
              })}
          </div>
        </div>
      </section>
    </div>
  );
}

interface DashboardStatProps {
  label: string;
  value: string;
  description: string;
  icon: React.ReactNode;
  index: number;
}

function DashboardStat({
  label,
  value,
  description,
  icon,
  index,
}: DashboardStatProps) {
  return (
    <motion.article
      className="stat-card"
      initial={{
        opacity: 0,
        y: 12,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      transition={{
        delay: index * 0.06,
      }}
    >
      <div className="stat-card-icon">{icon}</div>

      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        <small>{description}</small>
      </div>
    </motion.article>
  );
}
