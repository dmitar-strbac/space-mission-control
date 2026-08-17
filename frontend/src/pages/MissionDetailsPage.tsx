import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft,
  CalendarClock,
  Gauge,
  Orbit,
  Rocket,
  Satellite,
  Users,
} from "lucide-react";
import {
  Link,
  useParams,
} from "react-router-dom";

import {
  getMission,
  getMissionTimeline,
} from "../api/missionApi";
import { getSpacecraftById } from "../api/vehicleApi";
import { MissionStatusBadge } from "../components/mission/MissionStatusBadge";
import { MissionTimeline } from "../components/mission/MissionTimeline";
import {
  formatDateTime,
  formatLabel,
} from "../utils/formatters";
import { missionTypeLabels } from "../utils/mission";

export function MissionDetailsPage() {
  const { missionId } = useParams<{
    missionId: string;
  }>();

  const {
    data: mission,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["mission", missionId],
    queryFn: () => getMission(missionId!),
    enabled: Boolean(missionId),
  });

  const { data: timeline = [] } = useQuery({
    queryKey: ["mission-timeline", missionId],
    queryFn: () => getMissionTimeline(missionId!),
    enabled: Boolean(missionId),
  });

  const { data: spacecraft } = useQuery({
    queryKey: ["spacecraft", mission?.vehicle_id],
    queryFn: () =>
      getSpacecraftById(mission!.vehicle_id!),
    enabled: Boolean(mission?.vehicle_id),
  });

  if (isLoading) {
    return (
      <div className="detail-loading">
        Loading mission dossier...
      </div>
    );
  }

  if (isError || !mission) {
    return (
      <div className="content-error-state">
        <Orbit size={30} />
        <strong>Mission unavailable</strong>
        <p>
          The requested mission could not be loaded.
        </p>
      </div>
    );
  }

  const targetAltitude =
    typeof mission.target_parameters.target_altitude_km ===
    "number"
      ? mission.target_parameters.target_altitude_km
      : null;

  return (
    <div className="mission-details-page">
      <Link
        className="back-link"
        to="/missions"
      >
        <ArrowLeft size={15} />
        Mission Registry
      </Link>

      <section className="mission-detail-hero">
        <div>
          <span className="eyebrow">
            {missionTypeLabels[mission.mission_type]}
          </span>

          <h1>{mission.name}</h1>

          <div className="mission-detail-meta">
            <MissionStatusBadge
              status={mission.status}
            />

            <span>
              ID {mission.id.slice(0, 8).toUpperCase()}
            </span>
          </div>
        </div>

        {mission.status === "DRAFT" && (
          <Link
            className="primary-button page-action-button"
            to={`/missions/${mission.id}/prepare`}
          >
            <Rocket size={17} />
            Prepare Mission
          </Link>
        )}
      </section>

      {mission.failure_reason && (
        <div className="mission-failure-banner">
          <strong>Mission failure</strong>
          <span>{mission.failure_reason}</span>
        </div>
      )}

      <section className="mission-detail-grid">
        <article className="detail-panel">
          <div className="card-heading">
            <div>
              <span className="eyebrow">
                Mission Profile
              </span>
              <h2>Flight definition</h2>
            </div>

            <Orbit size={19} />
          </div>

          <div className="detail-data-grid">
            <DetailItem
              icon={<Gauge size={16} />}
              label="Target"
              value={
                targetAltitude !== null
                  ? `${targetAltitude} km orbit`
                  : formatLabel(
                      mission.target_type,
                    )
              }
            />

            <DetailItem
              icon={<Users size={16} />}
              label="Crew"
              value={`${mission.crew_count} member${
                mission.crew_count === 1 ? "" : "s"
              }`}
            />

            <DetailItem
              icon={<CalendarClock size={16} />}
              label="Planned Launch"
              value={formatDateTime(
                mission.planned_launch_time,
              )}
            />

            <DetailItem
              icon={<Satellite size={16} />}
              label="Simulation"
              value={`${mission.simulation_speed}× speed`}
            />
          </div>
        </article>

        <article className="detail-panel">
          <div className="card-heading">
            <div>
              <span className="eyebrow">
                Spacecraft
              </span>
              <h2>Assigned vehicle</h2>
            </div>

            <Satellite size={19} />
          </div>

          {spacecraft ? (
            <div className="assigned-spacecraft">
              <strong>{spacecraft.name}</strong>

              <span>
                {formatLabel(
                  spacecraft.vehicle_type,
                )}
              </span>

              <div>
                <small>STATUS</small>
                <b>
                  {formatLabel(spacecraft.status)}
                </b>
              </div>

              <div>
                <small>CREW CAPACITY</small>
                <b>{spacecraft.crew_capacity}</b>
              </div>
            </div>
          ) : (
            <div className="panel-empty">
              No spacecraft assigned.
            </div>
          )}
        </article>
      </section>

      <section className="detail-panel timeline-panel">
        <div className="card-heading">
          <div>
            <span className="eyebrow">
              Distributed Events
            </span>
            <h2>Mission timeline</h2>
          </div>
        </div>

        <MissionTimeline events={timeline} />
      </section>
    </div>
  );
}

interface DetailItemProps {
  icon: React.ReactNode;
  label: string;
  value: string;
}

function DetailItem({
  icon,
  label,
  value,
}: DetailItemProps) {
  return (
    <div className="detail-item">
      <div>{icon}</div>

      <span>
        <small>{label}</small>
        <strong>{value}</strong>
      </span>
    </div>
  );
}
