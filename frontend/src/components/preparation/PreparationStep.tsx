import {
  Check,
  Circle,
  LoaderCircle,
  RotateCcw,
  TriangleAlert,
} from "lucide-react";

import type {
  SagaStep,
  SagaStepStatus,
  SagaStepType,
} from "../../types/preparation";
import { formatDateTime } from "../../utils/formatters";

const stepLabels: Record<SagaStepType, string> = {
  VEHICLE_RESERVATION: "Spacecraft Reservation",
  TRAJECTORY_PLANNING: "Trajectory Planning",
  RESOURCE_VALIDATION: "Resource Validation",
  COMMUNICATION_PROFILE: "Communication Profile",
  SIMULATION_INITIALIZATION: "Simulation Initialization",
};

const stepServices: Record<SagaStepType, string> = {
  VEHICLE_RESERVATION: "Vehicle Service",
  TRAJECTORY_PLANNING: "Trajectory Service",
  RESOURCE_VALIDATION: "Vehicle Service",
  COMMUNICATION_PROFILE: "Communication Service",
  SIMULATION_INITIALIZATION: "Flight Dynamics Service",
};

interface PreparationStepProps {
  step: SagaStep;
  last: boolean;
}

function getStatusIcon(status: SagaStepStatus) {
  switch (status) {
    case "COMPLETED":
      return <Check size={17} />;

    case "IN_PROGRESS":
      return (
        <LoaderCircle
          className="preparation-spin"
          size={17}
        />
      );

    case "FAILED":
      return <TriangleAlert size={17} />;

    case "COMPENSATING":
    case "COMPENSATED":
      return <RotateCcw size={17} />;

    default:
      return <Circle size={13} />;
  }
}

export function PreparationStep({
  step,
  last,
}: PreparationStepProps) {
  const statusClass = step.status
    .toLowerCase()
    .replaceAll("_", "-");

  return (
    <div
      className={`preparation-step preparation-${statusClass}`}
    >
      <div className="preparation-step-track">
        <div className="preparation-step-marker">
          {getStatusIcon(step.status)}
        </div>

        {!last && (
          <div className="preparation-step-line" />
        )}
      </div>

      <div className="preparation-step-content">
        <div className="preparation-step-heading">
          <div>
            <strong>
              {stepLabels[step.step_type]}
            </strong>

            <span>
              {stepServices[step.step_type]}
            </span>
          </div>

          <span className="preparation-step-status">
            {step.status.replaceAll("_", " ")}
          </span>
        </div>

        {step.status === "IN_PROGRESS" && (
          <p>
            Distributed workflow step is currently
            executing.
          </p>
        )}

        {step.failure_reason && (
          <p className="preparation-step-failure">
            {step.failure_reason}
          </p>
        )}

        {step.completed_at && (
          <small>
            Completed{" "}
            {formatDateTime(step.completed_at)}
          </small>
        )}

        {step.compensated_at && (
          <small>
            Compensation completed{" "}
            {formatDateTime(step.compensated_at)}
          </small>
        )}
      </div>
    </div>
  );
}
