"""enforce_single_administrator

Revision ID: defc8f1e7616
Revises: 41cff515fbfd
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import context, op

revision: str = "defc8f1e7616"
down_revision: str | None = "41cff515fbfd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    if not context.is_offline_mode():
        owner = (
            op.get_bind()
            .execute(
                sa.text(
                    "SELECT value FROM service_state WHERE key = 'admin_telegram_id'"
                )
            )
            .scalar_one_or_none()
        )
        if owner is not None and (
            not owner.isascii() or not owner.isdecimal() or not 0 < int(owner) < 2**63
        ):
            raise RuntimeError(
                "Invalid persisted administrator identity; migration stopped"
            )
    op.create_table(
        "administrator",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.CheckConstraint("id = 1", name="ck_administrator_singleton"),
        sa.CheckConstraint("user_id > 0", name="ck_administrator_user_id_positive"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name=op.f("fk_administrator_user_id_user")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_administrator")),
        sa.UniqueConstraint("user_id", name=op.f("uq_administrator_user_id")),
    )
    op.execute(
        sa.text("""
        INSERT INTO user (id, name, created_at, last_seen_at)
        SELECT CAST(value AS INTEGER), 'Администратор', 0, 0
        FROM service_state
        WHERE key = 'admin_telegram_id'
          AND NOT EXISTS (SELECT 1 FROM user WHERE id = CAST(value AS INTEGER))
    """)
    )
    op.execute(
        sa.text("""
        INSERT INTO administrator (id, user_id, created_at)
        SELECT 1, CAST(value AS INTEGER), CAST(strftime('%s', 'now') AS INTEGER)
        FROM service_state WHERE key = 'admin_telegram_id'
    """)
    )
    op.execute(sa.text("DELETE FROM service_state WHERE key = 'admin_telegram_id'"))


def downgrade() -> None:
    op.execute(
        sa.text("""
        INSERT INTO service_state (key, value)
        SELECT 'admin_telegram_id', CAST(user_id AS TEXT)
        FROM administrator WHERE id = 1
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """)
    )
    op.drop_table("administrator")
