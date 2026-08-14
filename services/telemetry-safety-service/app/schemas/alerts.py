from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.enums import (
    AlertSeverity,
    AlertType,
    RecommendationType,
)


class DetectedAnomaly(BaseModel):
    alert_type: AlertType
    severity: AlertSeverity

    message: str

    measured_value: float | str
    threshold: float | str

    recommendation: RecommendationType | None = None


class AlertRecord(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
    )

    mission_id: UUID

    alert_type: AlertType
    severity: AlertSeverity

    message: str

    measured_value: float | str
    threshold: float | str

    created_at: datetime
    last_seen_at: datetime

    resolved_at: datetime | None = None


class AnomalyEvent(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
    )

    mission_id: UUID
    alert_id: UUID

    alert_type: AlertType
    severity: AlertSeverity

    measured_value: float | str
    threshold: float | str

    recommendation: RecommendationType | None

    created_at: datetime
