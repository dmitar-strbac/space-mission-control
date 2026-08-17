import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import {
  ArrowLeft,
  CheckCircle2,
  Orbit,
  RadioTower,
  Rocket,
  ShieldCheck,
  TriangleAlert,
} from "lucide-react";
import { useEffect, useState } from "react";
import {
  Link,
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  getMission,
  getMissionPreparation,
  launchMission,
  prepareMission,
} from "../api/missionApi";
import {
  getTrajectoryManeuvers,
  getTrajectoryPlan,
} from "../api/trajectoryApi";
import { TrajectoryAnalysis } from "../components/planning/TrajectoryAnalysis";
import { LaunchSequence } from "../components/preparation/LaunchSequence";
import { PreparationStep } from "../components/preparation/PreparationStep";
import { useAuth } from "../hooks/useAuth";
import type { SagaStep } from "../types/preparation";

export function PrepareMissionPage() {
  const { missionId } = useParams<{
    missionId: string;
  }>();

  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();

  const [showLaunchSequence, setShowLaunchSequence] =
    useState(false);

  const {
    data: mission,
    isLoading: missionLoading,
    isError: missionError,
  } = useQuery({
    queryKey: ["mission", missionId],
    queryFn: () => getMission(missionId!),
    enabled: Boolean(missionId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;

      return status === "PREPARING"
        ? 1_000
        : false;
    },
  });

  const shouldLoadPreparation =
    mission?.status === "PREPARING" ||
    mission?.status === "READY" ||
    mission?.status === "FAILED_PREPARATION";

  const {
    data: preparation,
  } = useQuery({
    queryKey: [
      "mission-preparation",
      missionId,
    ],
    queryFn: () =>
      getMissionPreparation(missionId!),
    enabled:
      Boolean(missionId) &&
      shouldLoadPreparation,
    refetchInterval:
      mission?.status === "PREPARING"
        ? 1_000
        : false,
  });

  const trajectoryEnabled =
    mission?.status === "READY" ||
    mission?.status === "IN_PROGRESS";

  const {
    data: trajectory,
  } = useQuery({
    queryKey: ["trajectory", missionId],
    queryFn: () =>
      getTrajectoryPlan(missionId!),
    enabled:
      Boolean(missionId) &&
      trajectoryEnabled,
  });

  const {
    data: maneuvers = [],
  } = useQuery({
    queryKey: [
      "trajectory-maneuvers",
      missionId,
    ],
    queryFn: () =>
      getTrajectoryManeuvers(missionId!),
    enabled:
      Boolean(missionId) &&
      trajectoryEnabled,
  });

  const prepareMutation = useMutation({
    mutationFn: () =>
      prepareMission(missionId!),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["mission", missionId],
      });

      await queryClient.invalidateQueries({
        queryKey: ["missions"],
      });
    },
  });

  const launchMutation = useMutation({
    mutationFn: () =>
      launchMission(missionId!),
    onSuccess: async () => {
      setShowLaunchSequence(true);

      await queryClient.invalidateQueries({
        queryKey: ["mission", missionId],
      });

      await queryClient.invalidateQueries({
        queryKey: ["missions"],
      });
    },
  });

  useEffect(() => {
    if (!showLaunchSequence) {
      return;
    }

    const timer = window.setTimeout(() => {
      navigate(`/missions/${missionId}`);
    }, 2_700);

    return () => {
      window.clearTimeout(timer);
    };
  }, [
    missionId,
    navigate,
    showLaunchSequence,
  ]);

  if (showLaunchSequence && mission) {
    return (
      <LaunchSequence
        missionName={mission.name}
      />
    );
  }

  if (missionLoading) {
    return (
      <div className="detail-loading">
        Loading mission preparation console...
      </div>
    );
  }

  if (
    missionError ||
    !mission ||
    !missionId
  ) {
    return (
      <div className="content-error-state">
        <Orbit size={30} />

        <strong>Mission unavailable</strong>

        <p>
          Mission preparation data could not be
          loaded.
        </p>
      </div>
    );
  }

  const targetAltitudeKm =
    typeof mission.target_parameters
      .target_altitude_km === "number"
      ? mission.target_parameters
          .target_altitude_km
      : 0;

  const steps: SagaStep[] =
    preparation?.steps ?? [];

  const completedSteps = steps.filter(
    (step) => step.status === "COMPLETED",
  ).length;

  const progress =
    steps.length > 0
      ? Math.round(
          (completedSteps / steps.length) * 100,
        )
      : 0;

  const operator =
    user?.role === "OPERATOR";

  return (
    <div className="prepare-mission-page">
      <Link
        className="back-link"
        to={`/missions/${mission.id}`}
      >
        <ArrowLeft size={15} />
        Mission Dossier
      </Link>

      <section className="preparation-hero">
        <div>
          <span className="eyebrow">
            Distributed Mission Preparation
          </span>

          <h1>{mission.name}</h1>

          <p>
            Mission Service coordinates spacecraft
            validation, trajectory planning, resource
            verification, communication setup and
            simulation initialization through the
            Prepare Mission Saga.
          </p>
        </div>

        <div className="preparation-hero-status">
          <span
            className={`preparation-mission-state state-${mission.status.toLowerCase()}`}
          >
            {mission.status.replaceAll("_", " ")}
          </span>

          {preparation?.saga_id && (
            <small>
              SAGA{" "}
              {preparation.saga_id
                .slice(0, 8)
                .toUpperCase()}
            </small>
          )}
        </div>
      </section>

      {mission.status === "DRAFT" && (
        <section className="prepare-init-card">
          <div className="prepare-init-icon">
            <RadioTower size={27} />
          </div>

          <div>
            <span className="eyebrow">
              Preparation Required
            </span>

            <h2>
              Ready to begin distributed validation
            </h2>

            <p>
              Starting preparation will reserve the
              assigned spacecraft and initiate the
              asynchronous Saga workflow across the
              mission services.
            </p>
          </div>

          <button
            className="primary-button preparation-action"
            type="button"
            disabled={
              !operator ||
              prepareMutation.isPending
            }
            onClick={() =>
              prepareMutation.mutate()
            }
          >
            <Rocket size={17} />

            {prepareMutation.isPending
              ? "Starting Saga..."
              : "Begin Preparation"}
          </button>

          {!operator && (
            <small className="observer-action-note">
              Operator authorization required.
            </small>
          )}
        </section>
      )}

      {prepareMutation.isError && (
        <div className="mission-operation-error">
          <TriangleAlert size={17} />

          Preparation could not be started. Verify
          mission configuration and service health.
        </div>
      )}

      {mission.status === "PREPARING" && (
        <section className="preparation-console">
          <div className="preparation-console-heading">
            <div>
              <span className="eyebrow">
                Saga Execution
              </span>

              <h2>
                Distributed preparation sequence
              </h2>
            </div>

            <div className="preparation-progress-value">
              <strong>{progress}%</strong>
              <span>
                {completedSteps}/{steps.length} steps
              </span>
            </div>
          </div>

          <div className="preparation-progress-track">
            <span
              style={{
                width: `${progress}%`,
              }}
            />
          </div>

          <div className="preparation-console-grid">
            <div className="preparation-steps">
              {steps.map((step, index) => (
                <PreparationStep
                  key={step.id}
                  step={step}
                  last={
                    index ===
                    steps.length - 1
                  }
                />
              ))}
            </div>

            <div className="preparation-network">
              <div className="preparation-network-core">
                <Orbit size={24} />
                <strong>
                  Mission Service
                </strong>
                <span>
                  Saga Orchestrator
                </span>
              </div>

              <div className="preparation-network-services">
                <span>Vehicle</span>
                <span>Trajectory</span>
                <span>Communication</span>
                <span>Flight Dynamics</span>
              </div>

              <p>
                Commands and results are exchanged
                asynchronously through NATS
                JetStream.
              </p>
            </div>
          </div>
        </section>
      )}

      {mission.status ===
        "FAILED_PREPARATION" && (
        <section className="preparation-failed-card">
          <TriangleAlert size={25} />

          <div>
            <span className="eyebrow">
              Preparation Failed
            </span>

            <h2>
              Mission configuration was rejected
            </h2>

            <p>
              {mission.failure_reason ??
                "The distributed preparation workflow could not be completed."}
            </p>
          </div>

          {steps.length > 0 && (
            <div className="preparation-failed-steps">
              {steps.map((step, index) => (
                <PreparationStep
                  key={step.id}
                  step={step}
                  last={
                    index ===
                    steps.length - 1
                  }
                />
              ))}
            </div>
          )}
        </section>
      )}

      {mission.status === "READY" &&
        trajectory && (
          <>
            <section className="mission-ready-banner">
              <div className="mission-ready-icon">
                <CheckCircle2 size={25} />
              </div>

              <div>
                <span className="eyebrow">
                  Mission Ready
                </span>

                <h2>
                  All preparation checks completed
                </h2>

                <p>
                  Spacecraft, trajectory, resources,
                  communication profile and simulation
                  state have been successfully
                  validated.
                </p>
              </div>

              <div className="mission-ready-security">
                <ShieldCheck size={18} />
                FLIGHT AUTHORIZATION AVAILABLE
              </div>
            </section>

            <TrajectoryAnalysis
              trajectory={trajectory}
              maneuvers={maneuvers}
              targetAltitudeKm={
                targetAltitudeKm
              }
            />

            <section className="launch-authorization-card">
              <div>
                <span className="eyebrow">
                  Final Authorization
                </span>

                <h2>
                  Mission cleared for orbital
                  simulation
                </h2>

                <p>
                  Launch authorization transitions
                  the prepared mission into active
                  simulation. Real-time controls and
                  telemetry are handled by the Mission
                  Control interface.
                </p>
              </div>

              <button
                className="primary-button launch-authorization-button"
                type="button"
                disabled={
                  !operator ||
                  launchMutation.isPending
                }
                onClick={() =>
                  launchMutation.mutate()
                }
              >
                <Rocket size={19} />

                {launchMutation.isPending
                  ? "Authorizing..."
                  : "Authorize Mission Launch"}
              </button>
            </section>

            {launchMutation.isError && (
              <div className="mission-operation-error">
                <TriangleAlert size={17} />

                Mission launch authorization failed.
              </div>
            )}
          </>
        )}

      {mission.status === "IN_PROGRESS" &&
        trajectory && (
          <section className="mission-active-card">
            <CheckCircle2 size={24} />

            <div>
              <span className="eyebrow">
                Mission Active
              </span>

              <h2>
                Orbital simulation in progress
              </h2>

              <p>
                The mission is now active. Real-time
                controls and telemetry will be
                available from the Mission Control
                interface in the next frontend
                milestone.
              </p>
            </div>
          </section>
        )}
    </div>
  );
}
