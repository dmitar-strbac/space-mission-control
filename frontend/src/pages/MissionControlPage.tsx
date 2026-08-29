import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  Activity,
  ArrowLeft,
  BatteryCharging,
  Fuel,
  Gauge,
  Orbit,
  RadioTower,
  Rocket,
  ShieldCheck,
  TimerReset,
  Wind,
} from "lucide-react";

import {
  Link,
  useParams,
} from "react-router-dom";

import {
  getMission,
  launchMission,
} from "../api/missionApi";

import {
  getSimulation,
  getSimulationState,
  startSimulation
} from "../api/simulationApi";

import {
  TelemetryMetric,
} from "../components/control/TelemetryMetric";

import {
  MissionStatusBadge,
} from "../components/mission/MissionStatusBadge";

import { useAuth } from "../hooks/useAuth";

import {
  useMissionTelemetry,
} from "../hooks/useMissionTelemetry";

import {
  formatLabel,
} from "../utils/formatters";

function resourceTone(value: number) {
  if (value <= 15) {
    return "critical" as const;
  }

  if (value <= 30) {
    return "caution" as const;
  }

  return "nominal" as const;
}

function formatMissionTime(
  seconds: number,
) {
  const totalSeconds = Math.max(
    0,
    Math.floor(seconds),
  );

  const hours =
    Math.floor(totalSeconds / 3600);

  const minutes =
    Math.floor(
      (totalSeconds % 3600) / 60,
    );

  const remainingSeconds =
    totalSeconds % 60;

  return (
    `T+${String(hours).padStart(2, "0")}:` +
    `${String(minutes).padStart(2, "0")}:` +
    `${String(remainingSeconds).padStart(2, "0")}`
  );
}

export function MissionControlPage() {
  const { missionId } =
    useParams<{
      missionId: string;
    }>();

  const queryClient =
    useQueryClient();

  const { user } =
    useAuth();

  const missionQuery = useQuery({
    queryKey: [
      "mission",
      missionId,
    ],

    queryFn: () =>
      getMission(missionId!),

    enabled:
      Boolean(missionId),

    refetchInterval: 5_000,
  });

  const simulationQuery =
    useQuery({
      queryKey: [
        "simulation",
        missionId,
      ],

      queryFn: () =>
        getSimulation(
          missionId!,
        ),

      enabled:
        Boolean(missionId),

      refetchInterval: 5_000,
    });

  const simulationStateQuery =
    useQuery({
      queryKey: [
        "simulation-state",
        missionId,
      ],

      queryFn: () =>
        getSimulationState(
          missionId!,
        ),

      enabled:
        Boolean(missionId),
    });

  const {
    telemetry,
    latestTelemetry,
    alerts,
    socketStatus,
  } =
    useMissionTelemetry(
      missionId,
    );

  const launchMutation =
    useMutation({
      mutationFn:
        async () => {
          if (!missionId) {
            throw new Error(
              "Mission id is required.",
            );
          }

          await launchMission(
            missionId,
          );

          return startSimulation(
            missionId,
          );
        },

      onSuccess:
        async () => {
          await Promise.all([
            queryClient
              .invalidateQueries({
                queryKey: [
                  "mission",
                  missionId,
                ],
              }),

            queryClient
              .invalidateQueries({
                queryKey: [
                  "simulation",
                  missionId,
                ],
              }),
          ]);
        },
    });


  if (
    missionQuery.isLoading ||
    simulationQuery.isLoading
  ) {
    return (
      <div className="detail-loading">
        Initializing mission control
        console...
      </div>
    );
  }

  const mission =
    missionQuery.data;

  const simulation =
    simulationQuery.data;

  if (!mission || !simulation) {
    return (
      <div className="content-error-state">
        <Orbit size={30} />

        <strong>
          Mission control unavailable
        </strong>

        <p>
          The mission has not completed
          preparation or its simulation
          session could not be loaded.
        </p>
      </div>
    );
  }

  const isOperator =
    user?.role === "OPERATOR";

  const currentState =
    simulationStateQuery.data;

  const simulationTime =
    latestTelemetry
      ?.simulation_time_s ??
    currentState
      ?.elapsed_time_s ??
    0;

  const criticalAlerts =
    alerts.filter(
      (alert) =>
        alert.severity ===
          "CRITICAL" &&
        alert.resolved_at ===
          null,
    ).length;

  const communication =
    latestTelemetry
      ?.communication;

  return (
    <div className="mission-control-page">
      <Link
        className="back-link"
        to={`/missions/${mission.id}`}
      >
        <ArrowLeft size={15} />

        Mission Dossier
      </Link>

      <section className="mission-control-hero">
        <div>
          <span className="eyebrow">
            Live Mission Control
          </span>

          <h1>
            {mission.name}
          </h1>

          <div className="mission-control-meta">
            <MissionStatusBadge
              status={
                mission.status
              }
            />

            <span>
              {formatMissionTime(
                simulationTime,
              )}
            </span>

            <span>
              {
                mission
                  .simulation_speed
              }
              × SIM RATE
            </span>
          </div>
        </div>

        <div className="mission-control-link-state">
          <span
            className={
              `control-link-dot ` +
              `control-link-${socketStatus}`
            }
          />

          <div>
            <small>
              TELEMETRY LINK
            </small>

            <strong>
              {formatLabel(
                socketStatus,
              )}
            </strong>
          </div>
        </div>
      </section>

      {mission.status ===
        "READY" && (
        <section className="launch-control-banner">
          <div className="launch-control-icon">
            <Rocket
              size={24}
            />
          </div>

          <div>
            <span className="eyebrow">
              Flight Ready
            </span>

            <h2>
              Mission is cleared
              for simulation start
            </h2>

            <p>
              Launching transitions
              the mission to active
              operations and starts
              the prepared Flight
              Dynamics session.
            </p>
          </div>

          <button
            className={
              "primary-button " +
              "control-primary-action"
            }
            type="button"
            disabled={
              !isOperator ||
              launchMutation
                .isPending
            }
            onClick={() =>
              launchMutation
                .mutate()
            }
          >
            <Rocket size={17} />

            {launchMutation
              .isPending
              ? "Starting Mission..."
              : "Launch Mission"}
          </button>
        </section>
      )}

      {launchMutation.isError && (
        <div className="mission-operation-error">
          Mission start failed.
          Verify Mission Service
          and Flight Dynamics
          readiness.
        </div>
      )}

      <section className="mission-control-summary-grid">
        <article className="control-status-card">
          <div className="card-heading">
            <div>
              <span className="eyebrow">
                Flight State
              </span>

              <h2>
                Mission status
              </h2>
            </div>

            <Activity
              size={19}
            />
          </div>

          <div className="control-status-values">
            <div>
              <small>
                MISSION
              </small>

              <strong>
                {formatLabel(
                  mission.status,
                )}
              </strong>
            </div>

            <div>
              <small>
                PHASE
              </small>

              <strong>
                {mission
                  .mission_phase
                  ? formatLabel(
                      mission
                        .mission_phase,
                    )
                  : "Awaiting phase"}
              </strong>
            </div>

            <div>
              <small>
                SIMULATION
              </small>

              <strong>
                {formatLabel(
                  simulation
                    .status,
                )}
              </strong>
            </div>
          </div>
        </article>

        <article className="control-status-card">
          <div className="card-heading">
            <div>
              <span className="eyebrow">
                Safety State
              </span>

              <h2>
                Operational envelope
              </h2>
            </div>

            <ShieldCheck
              size={19}
            />
          </div>

          <div className="control-safety-line">
            <span
              className={
                criticalAlerts >
                0
                  ? "safety-critical"
                  : "safety-nominal"
              }
            >
              {criticalAlerts >
              0
                ? criticalAlerts
                : "NOMINAL"}
            </span>

            <p>
              {criticalAlerts >
              0
                ? "Critical alerts require operator attention."
                : "No unresolved critical safety alerts detected."}
            </p>
          </div>
        </article>
      </section>

      <section className="telemetry-section-heading">
        <div>
          <span className="eyebrow">
            Real-time Telemetry
          </span>

          <h2>
            Spacecraft systems
          </h2>
        </div>

        <span className="telemetry-sample-count">
          {telemetry.length}{" "}
          buffered samples
        </span>
      </section>

      <section className="telemetry-metric-grid">
        <TelemetryMetric
          icon={
            <Gauge
              size={17}
            />
          }
          label="Orbital Altitude"
          value={
            latestTelemetry
              ? `${latestTelemetry.navigation.altitude_km.toFixed(2)} km`
              : "—"
          }
          detail={
            latestTelemetry
              ? `${latestTelemetry.navigation.vertical_speed_m_s.toFixed(1)} m/s vertical`
              : "Waiting for telemetry"
          }
        />

        <TelemetryMetric
          icon={
            <Orbit
              size={17}
            />
          }
          label="Velocity"
          value={
            latestTelemetry
              ? `${latestTelemetry.navigation.speed_km_s.toFixed(3)} km/s`
              : "—"
          }
          detail={
            latestTelemetry
              ?.navigation
              .trajectory_deviation_km !=
            null
              ? `${latestTelemetry.navigation.trajectory_deviation_km.toFixed(3)} km deviation`
              : "Nominal trajectory reference"
          }
        />

        <TelemetryMetric
          icon={
            <Fuel
              size={17}
            />
          }
          label="Propellant"
          value={
            latestTelemetry
              ? `${latestTelemetry.propulsion.propellant_percent.toFixed(1)}%`
              : "—"
          }
          detail={
            latestTelemetry
              ? `${latestTelemetry.propulsion.propellant_kg.toFixed(1)} kg remaining`
              : "Waiting for telemetry"
          }
          progress={
            latestTelemetry
              ?.propulsion
              .propellant_percent
          }
          tone={resourceTone(
            latestTelemetry
              ?.propulsion
              .propellant_percent ??
              100,
          )}
        />

        <TelemetryMetric
          icon={
            <Wind
              size={17}
            />
          }
          label="Oxygen"
          value={
            latestTelemetry
              ? `${latestTelemetry.life_support.oxygen_percent.toFixed(1)}%`
              : "—"
          }
          detail={
            latestTelemetry
              ?.life_support
              .estimated_oxygen_remaining_h !=
            null
              ? `${latestTelemetry.life_support.estimated_oxygen_remaining_h.toFixed(1)} h estimated`
              : "Consumption model active"
          }
          progress={
            latestTelemetry
              ?.life_support
              .oxygen_percent
          }
          tone={resourceTone(
            latestTelemetry
              ?.life_support
              .oxygen_percent ??
              100,
          )}
        />

        <TelemetryMetric
          icon={
            <BatteryCharging
              size={17}
            />
          }
          label="Electrical Power"
          value={
            latestTelemetry
              ? `${latestTelemetry.power.battery_percent.toFixed(1)}%`
              : "—"
          }
          detail={
            latestTelemetry
              ? `${latestTelemetry.power.battery_kwh.toFixed(2)} kWh available`
              : "Waiting for telemetry"
          }
          progress={
            latestTelemetry
              ?.power
              .battery_percent
          }
          tone={resourceTone(
            latestTelemetry
              ?.power
              .battery_percent ??
              100,
          )}
        />

        <TelemetryMetric
          icon={
            <RadioTower
              size={17}
            />
          }
          label="Communication"
          value={
            communication
              ? formatLabel(
                  communication
                    .signal_status,
                )
              : "—"
          }
          detail={
            communication
              ? `${communication.one_way_delay_ms.toFixed(1)} ms one-way · ${communication.packet_loss_percent.toFixed(1)}% loss`
              : "Awaiting communication state"
          }
          tone={
            communication
              ?.signal_status ===
            "LOST"
              ? "critical"
              : communication
                    ?.signal_status ===
                  "DEGRADED"
                ? "caution"
                : "nominal"
          }
        />

        <TelemetryMetric
          icon={
            <TimerReset
              size={17}
            />
          }
          label="Mission Elapsed"
          value={formatMissionTime(
            simulationTime,
          )}
          detail={
            `${mission.simulation_speed}× ` +
            "simulation acceleration"
          }
        />

        <TelemetryMetric
          icon={
            <Activity
              size={17}
            />
          }
          label="Remaining Delta-v"
          value={
            latestTelemetry
              ? `${latestTelemetry.propulsion.remaining_delta_v_m_s.toFixed(0)} m/s`
              : "—"
          }
          detail={
            latestTelemetry
              ?.propulsion
              .engine_thrust_n
              ? `${latestTelemetry.propulsion.engine_thrust_n.toFixed(0)} N current thrust`
              : "Engine idle"
          }
        />
      </section>
    </div>
  );
}
