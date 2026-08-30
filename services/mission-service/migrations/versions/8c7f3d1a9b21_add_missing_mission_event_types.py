"""add missing mission event types

Revision ID: 8c7f3d1a9b21
Revises: 4a6c54768902
Create Date: 2026-08-30

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8c7f3d1a9b21"
down_revision: str | Sequence[str] | None = "4a6c54768902"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add mission event values introduced after the initial schema."""

    op.execute(
        """
        ALTER TYPE mission_event_type
        ADD VALUE IF NOT EXISTS 'PREPARATION_FAILED'
        """
    )

    op.execute(
        """
        ALTER TYPE mission_event_type
        ADD VALUE IF NOT EXISTS 'MISSION_ABORTED'
        """
    )


def downgrade() -> None:
    """PostgreSQL enum values are intentionally retained on downgrade."""
    pass
