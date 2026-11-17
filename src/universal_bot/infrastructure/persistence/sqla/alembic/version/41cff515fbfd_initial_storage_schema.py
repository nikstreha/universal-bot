"""initial_storage_schema

Revision ID: 41cff515fbfd
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "41cff515fbfd"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade():
    op.create_table(
        "admin_dialog",
        sa.Column("admin_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=False),
        sa.Column("payload", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("admin_id", name=op.f("pk_admin_dialog")),
    )
    op.create_table(
        "audit_event",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_event")),
    )
    op.create_table(
        "delivery",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("dedup_key", sa.String(), nullable=False),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column("next_attempt_at", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("reply_to", sa.Integer(), nullable=True),
        sa.Column("filename", sa.String(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("lease_until", sa.Integer(), nullable=True),
        sa.Column("message_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_delivery")),
        sa.UniqueConstraint("dedup_key", name=op.f("uq_delivery_dedup_key")),
    )
    op.create_table(
        "job",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("resource_id", sa.String(), nullable=False),
        sa.Column("dedup_key", sa.String(), nullable=False),
        sa.Column("next_attempt_at", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("lease_until", sa.Integer(), nullable=True),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("error", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_job")),
        sa.UniqueConstraint("dedup_key", name=op.f("uq_job_dedup_key")),
    )
    with op.batch_alter_table("job", schema=None) as batch_op:
        batch_op.create_index(
            "ix_job_queue", ["kind", "state", "next_attempt_at"], unique=False
        )
    op.create_table(
        "rate_limit",
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("window_start", sa.Integer(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("key", name=op.f("pk_rate_limit")),
    )
    op.create_table(
        "service_state",
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("key", name=op.f("pk_service_state")),
    )
    op.create_table(
        "telegram_update",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payload", sa.String(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_telegram_update")),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("last_seen_at", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user")),
    )
    op.create_table(
        "access_request",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("decided_at", sa.Integer(), nullable=True),
        sa.Column("decided_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name=op.f("fk_access_request_user_id_user")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_access_request")),
        sa.UniqueConstraint("user_id", name=op.f("uq_access_request_user_id")),
    )
    op.create_table(
        "admin_notification",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("event_key", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("outcome", sa.String(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("read_at", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name=op.f("fk_admin_notification_user_id_user")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_admin_notification")),
        sa.UniqueConstraint("event_key", name=op.f("uq_admin_notification_event_key")),
    )
    op.create_table(
        "auth_attempt",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("challenge", sa.String(), nullable=False),
        sa.Column("login_code", sa.String(), nullable=False),
        sa.Column("installation_id", sa.String(), nullable=False),
        sa.Column("device_name", sa.String(), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("consumed_at", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["candidate_id"],
            ["user.id"],
            name=op.f("fk_auth_attempt_candidate_id_user"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name=op.f("fk_auth_attempt_user_id_user")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_attempt")),
    )
    op.create_table(
        "session",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("installation_id", sa.String(), nullable=False),
        sa.Column("device_name", sa.String(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("last_seen_at", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=False),
        sa.Column("absolute_expires_at", sa.Integer(), nullable=False),
        sa.Column("revoked_at", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name=op.f("fk_session_user_id_user")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_session")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_session_token_hash")),
    )
    op.create_table(
        "transcription",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("telegram_file_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("text", sa.String(), nullable=True),
        sa.Column("error", sa.String(), nullable=True),
        sa.Column("delivered_message_id", sa.Integer(), nullable=True),
        sa.Column("finished_at", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["user.id"], name=op.f("fk_transcription_owner_id_user")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_transcription")),
        sa.UniqueConstraint(
            "chat_id", "message_id", name=op.f("uq_transcription_chat_id")
        ),
    )
    op.create_table(
        "upload",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("operation_key", sa.String(), nullable=False),
        sa.Column("original_name", sa.String(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(), nullable=False),
        sa.Column("declared_mime", sa.String(), nullable=False),
        sa.Column("storage_date", sa.String(), nullable=False),
        sa.Column("storage_timezone", sa.String(), nullable=False),
        sa.Column("part_bytes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("file_id", sa.String(), nullable=True),
        sa.Column("error", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["user.id"], name=op.f("fk_upload_owner_id_user")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_upload")),
        sa.UniqueConstraint(
            "owner_id", "operation_key", name=op.f("uq_upload_owner_id")
        ),
    )
    op.create_table(
        "whitelist",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("added_at", sa.Integer(), nullable=False),
        sa.Column("added_by", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name=op.f("fk_whitelist_user_id_user")
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_whitelist")),
    )
    op.create_table(
        "file",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("upload_id", sa.String(), nullable=False),
        sa.Column("object_key", sa.String(), nullable=False),
        sa.Column("original_name", sa.String(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(), nullable=False),
        sa.Column("storage_date", sa.String(), nullable=False),
        sa.Column("storage_timezone", sa.String(), nullable=False),
        sa.Column("mime_type", sa.String(), nullable=False),
        sa.Column("media_kind", sa.String(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("checked_at", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("trashed_at", sa.Integer(), nullable=True),
        sa.Column("purge_after", sa.Integer(), nullable=True),
        sa.Column("integrity", sa.String(), nullable=False),
        sa.Column("thumbnail_key", sa.String(), nullable=True),
        sa.Column("thumbnail_state", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["user.id"], name=op.f("fk_file_owner_id_user")
        ),
        sa.ForeignKeyConstraint(
            ["upload_id"], ["upload.id"], name=op.f("fk_file_upload_id_upload")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_file")),
        sa.UniqueConstraint("object_key", name=op.f("uq_file_object_key")),
        sa.UniqueConstraint("upload_id", name=op.f("uq_file_upload_id")),
    )
    with op.batch_alter_table("file", schema=None) as batch_op:
        batch_op.create_index(
            "ix_file_catalog",
            ["owner_id", "state", "storage_date", "created_at", "id"],
            unique=False,
        )
    op.create_table(
        "upload_part",
        sa.Column("upload_id", sa.String(), nullable=False),
        sa.Column("part_index", sa.Integer(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(), nullable=False),
        sa.Column("object_key", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["upload_id"], ["upload.id"], name=op.f("fk_upload_part_upload_id_upload")
        ),
        sa.PrimaryKeyConstraint("upload_id", "part_index", name=op.f("pk_upload_part")),
    )
    op.create_table(
        "verification",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("file_id", sa.String(), nullable=False),
        sa.Column("operation_key", sa.String(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("checked_at", sa.Integer(), nullable=True),
        sa.Column("observed_sha256", sa.String(), nullable=True),
        sa.Column("observed_size", sa.Integer(), nullable=True),
        sa.Column("integrity", sa.String(), nullable=True),
        sa.Column("error", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["file_id"], ["file.id"], name=op.f("fk_verification_file_id_file")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_verification")),
        sa.UniqueConstraint(
            "file_id", "operation_key", name=op.f("uq_verification_file_id")
        ),
    )


def downgrade():
    op.drop_table("verification")
    op.drop_table("upload_part")
    with op.batch_alter_table("file", schema=None) as batch_op:
        batch_op.drop_index("ix_file_catalog")
    op.drop_table("file")
    op.drop_table("whitelist")
    op.drop_table("upload")
    op.drop_table("transcription")
    op.drop_table("session")
    op.drop_table("auth_attempt")
    op.drop_table("admin_notification")
    op.drop_table("access_request")
    op.drop_table("user")
    op.drop_table("telegram_update")
    op.drop_table("service_state")
    op.drop_table("rate_limit")
    with op.batch_alter_table("job", schema=None) as batch_op:
        batch_op.drop_index("ix_job_queue")
    op.drop_table("job")
    op.drop_table("delivery")
    op.drop_table("audit_event")
    op.drop_table("admin_dialog")
