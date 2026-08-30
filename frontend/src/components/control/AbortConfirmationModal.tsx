import {
  AlertTriangle,
  X,
} from "lucide-react";

interface AbortConfirmationModalProps {
  missionName: string;
  pending: boolean;

  onConfirm: () => void;
  onCancel: () => void;
}

export function AbortConfirmationModal({
  missionName,
  pending,
  onConfirm,
  onCancel,
}: AbortConfirmationModalProps) {
  return (
    <div
      className="abort-modal-backdrop"
      role="presentation"
      onMouseDown={
        pending
          ? undefined
          : onCancel
      }
    >
      <section
        className="abort-confirmation-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="abort-confirmation-title"
        onMouseDown={(
          event,
        ) =>
          event
            .stopPropagation()
        }
      >
        <button
          className="abort-modal-close"
          type="button"
          disabled={pending}
          onClick={onCancel}
          aria-label="Close abort confirmation"
        >
          <X size={17} />
        </button>

        <div className="abort-modal-icon">
          <AlertTriangle
            size={26}
          />
        </div>

        <span className="eyebrow">
          Emergency Procedure
        </span>

        <h2 id="abort-confirmation-title">
          Confirm mission abort
        </h2>

        <p>
          You are about to initiate
          an Emergency Abort for{" "}
          <strong>
            {missionName}
          </strong>
          .
        </p>

        <div className="abort-modal-warning">
          This command will cancel
          nominal maneuver execution
          and begin the distributed
          safe-return workflow.
        </div>

        <div className="abort-modal-actions">
          <button
            className="secondary-button"
            type="button"
            disabled={pending}
            onClick={onCancel}
          >
            Cancel
          </button>

          <button
            className="abort-modal-confirm"
            type="button"
            disabled={pending}
            onClick={onConfirm}
          >
            <AlertTriangle
              size={16}
            />

            {pending
              ? "Initiating Abort..."
              : "Confirm Emergency Abort"}
          </button>
        </div>
      </section>
    </div>
  );
}
