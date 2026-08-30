import {
  AlertTriangle,
  Check,
  CircleDot,
  Rocket,
} from "lucide-react";

import type { MissionEvent } from "../../types/mission";
import {
  formatDateTime,
  formatLabel,
} from "../../utils/formatters";

interface MissionTimelineProps {
  events: MissionEvent[];
}

function getEventIcon(eventType: MissionEvent["event_type"]) {
  if (
    eventType === "MISSION_FAILED" ||
    eventType === "PREPARATION_FAILED"
  ) {
    return <AlertTriangle size={15} />;
  }

  if (
    eventType === "MISSION_COMPLETED" ||
    eventType === "MISSION_ABORTED"
  ) {
    return <Check size={15} />;
  }

  if (eventType === "MISSION_STARTED") {
    return <Rocket size={15} />;
  }

  return <CircleDot size={14} />;
}

export function MissionTimeline({
  events,
}: MissionTimelineProps) {
  if (events.length === 0) {
    return (
      <div className="timeline-empty">
        No mission events have been recorded yet.
      </div>
    );
  }

  return (
    <div className="mission-timeline">
      {events.map((event) => (
        <div className="timeline-event" key={event.id}>
          <div className="timeline-marker">
            {getEventIcon(event.event_type)}
          </div>

          <div className="timeline-event-content">
            <div>
              <strong>
                {formatLabel(event.event_type)}
              </strong>

              <time>
                {formatDateTime(event.occurred_at)}
              </time>
            </div>

            <span>{formatLabel(event.source)}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
