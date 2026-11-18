"""Keep one editable Telegram response per transcription."""

import sqlalchemy as sa
from alembic import op

revision = "74c1be9ef203"
down_revision = "defc8f1e7616"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "transcription",
        "delivered_message_id",
        new_column_name="response_message_id",
        existing_type=sa.Integer(),
    )


def downgrade() -> None:
    op.alter_column(
        "transcription",
        "response_message_id",
        new_column_name="delivered_message_id",
        existing_type=sa.Integer(),
    )
