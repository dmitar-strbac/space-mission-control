import {
  AlertOctagon,
  Pause,
  Play,
  ShieldAlert,
} from "lucide-react";

import type {
  SimulationStatus,
} from "../../types/simulation";

interface MissionOperationsPanelProps {
  missionStatus: string;
  simulationStatus:
    SimulationStatus;
  isOperator: boolean;

  operationPending: boolean;
  operationError: boolean;

  onPause: () => void;
  onResume: () => void;
  onAbort: () => void;
}

export function MissionOperationsPanel({
  missionStatus,
  simulationStatus,
  isOperator,
  operationPending,
  operationError,
  onPause,
  onResume,
  onAbort,
}: MissionOperationsPanelProps) {
  const activeMission =
    missionStatus ===
      "IN_PROGRESS" ||
    missionStatus ===
      "ABORTING";

  const canPause =
    isOperator &&
    missionStatus ===
      "IN_PROGRESS" &&
    simulationStatus ===
      "RUNNING";

  const canResume =
    isOperator &&
    missionStatus ===
      "IN_PROGRESS" &&
    simulationStatus ===
      "PAUSED";

  const canAbort =
    isOperator &&
    missionStatus ===
      "IN_PROGRESS";

  return (
    <article className="mission-operations-panel">
      <div className="mission-operations-heading">
        <div>
          <span className="eyebrow">
            Command Interface
          </span>

          <h2>
            Flight operations
          </h2>

          <p>
            Operator controls are
            routed through the
            mission control backend.
          </p>
        </div>

        <span
          className={
            activeMission
              ? "operations-state-live"
              : "operations-state-idle"
          }
        >
          {activeMission
            ? "CONTROL ACTIVE"
            : "STANDBY"}
        </span>
      </div>

      <div className="mission-operation-actions">
        <button
          className="mission-command-button"
          type="button"
          disabled={
            !canPause ||
            operationPending
          }
          onClick={onPause}
        >
          <Pause size={18} />

          <span>
            <strong>
              Pause Simulation
            </strong>

            <small>
              Hold physical
              progression
            </small>
          </span>
        </button>

        <button
          className="mission-command-button"
          type="button"
          disabled={
            !canResume ||
            operationPending
          }
          onClick={onResume}
        >
          <Play size={18} />

          <span>
            <strong>
              Resume Simulation
            </strong>

            <small>
              Continue mission
              propagation
            </small>
          </span>
        </button>
      </div>

      <div className="mission-emergency-zone">
        <div>
          <ShieldAlert
            size={20}
          />

          <span>
            <strong>
              Emergency response
            </strong>

            <small>
              Initiates the
              distributed abort
              workflow.
            </small>
          </span>
        </div>

        <button
          className="mission-abort-button"
          type="button"
          disabled={
            !canAbort ||
            operationPending
          }
          onClick={onAbort}
        >
          <AlertOctagon
            size={17}
          />

          EMERGENCY ABORT
        </button>
      </div>

      {!isOperator && (
        <div className="mission-operation-observer-note">
          Observer accounts have
          read-only access to live
          mission operations.
        </div>
      )}

      {operationError && (
        <div className="mission-operation-error">
          Mission command failed.
          Verify service health and
          current simulation state.
        </div>
      )}
    </article>
  );
}
