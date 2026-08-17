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
import { Link } from "react-router-dom";

import { getServicesHealth } from "../api/healthApi";
import { getMissions } from "../api/missionApi";
import { MissionStatusBadge } from "../components/mission/MissionStatusBadge";
import { useAuth } from "../hooks/useAuth";
import { formatDateTime } from "../utils/formatters";
import { countMissionsByStatus } from "../utils/mission";

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

  const services = Object.entries(
    healthData?.services ?? {},
  );

  const healthyServices = services.filter(
    ([, service]) => service.status === "healthy",
  ).length;

  const {
    data: missionData,
    isLoading: missionsLoading,
  } = useQuery({
    queryKey: ["missions", "dashboard"],
    queryFn: () =>
      getMissions({
        limit: 100,
      }),
  });

  const missions = missionData?.items ?? [];

  const recentMissions = [...missions]
    .sort(
      (left, right) =>
        new Date(right.created_at).getTime() -
        new Date(left.created_at).getTime(),
    )
    .slice(0, 5);

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
          value={
            missionsLoading
              ? "—"
              : String(missionData?.total ?? 0)
          }
          description="Mission registry"
          icon={<Rocket size={20} />}
          index={0}
        />

        <DashboardStat
          label="Preparing"
          value={
            missionsLoading
              ? "—"
              : String(
                  countMissionsByStatus(
                    missions,
                    "PREPARING",
                  ),
                )
          }
          description="Saga workflows"
          icon={<Orbit size={20} />}
          index={1}
        />

        <DashboardStat
          label="Ready"
          value={
            missionsLoading
              ? "—"
              : String(
                  countMissionsByStatus(
                    missions,
                    "READY",
                  ),
                )
          }
          description="Cleared for launch"
          icon={<CircleCheck size={20} />}
          index={2}
        />

        <DashboardStat
          label="Active"
          value={
            missionsLoading
              ? "—"
              : String(
                  countMissionsByStatus(
                    missions,
                    "IN_PROGRESS",
                  ),
                )
          }
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

          {recentMissions.length === 0 ? (
            <div className="dashboard-empty-state">
              <Orbit size={34} />

              <strong>No missions registered</strong>

              <p>
                Create the first orbital mission to begin
                planning operations.
              </p>
            </div>
          ) : (
            <div className="recent-mission-list">
              {recentMissions.map((mission) => (
                <Link
                  className="recent-mission-row"
                  key={mission.id}
                  to={`/missions/${mission.id}`}
                >
                  <div className="recent-mission-identity">
                    <div className="recent-mission-icon">
                      <Orbit size={16} />
                    </div>

                    <div>
                      <strong>{mission.name}</strong>

                      <span>
                        Created{" "}
                        {formatDateTime(
                          mission.created_at,
                        )}
                      </span>
                    </div>
                  </div>

                  <MissionStatusBadge
                    status={mission.status}
                  />
                </Link>
              ))}
            </div>
          )}
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
              services.map(([serviceName, service]) => {
                const healthy =
                  service.status === "healthy";

                return (
                  <div
                    className="service-row"
                    key={serviceName}
                  >
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
                          {serviceDisplayNames[serviceName] ??
                            serviceName}
                        </strong>

                        <span>
                          Circuit {service.circuit_state}
                        </span>
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
