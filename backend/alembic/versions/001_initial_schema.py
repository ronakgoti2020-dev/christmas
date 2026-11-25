"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-11-25
"""

from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255)),
        sa.Column("profile_image", sa.String(500)),
        sa.Column("country", sa.String(80)),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("google_sub", sa.String(255), unique=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "groups",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("slug", sa.String(180), nullable=False, unique=True),
        sa.Column("description", sa.Text()),
        sa.Column("event_type", sa.String(40), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("registration_deadline", sa.Date(), nullable=False),
        sa.Column("minimum_budget", sa.Numeric(10, 2), nullable=False),
        sa.Column("maximum_budget", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(8), nullable=False),
        sa.Column("country", sa.String(80), nullable=False),
        sa.Column("exchange_type", sa.String(40), nullable=False),
        sa.Column("privacy_mode", sa.String(40), nullable=False),
        sa.Column("visibility", sa.String(40), nullable=False),
        sa.Column("organizer_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("invite_code", sa.String(180), nullable=False, unique=True),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("assignment_status", sa.String(40), nullable=False),
        sa.Column("reveal_identities", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("theme", sa.String(40), nullable=False, server_default="christmas"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "group_participants",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("group_id", sa.String(36), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.String(40), nullable=False),
        sa.Column("participation_status", sa.String(40), nullable=False),
        sa.Column("wishlist_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("gift_preferences", sa.Text()),
        sa.Column("interests", sa.Text()),
        sa.Column("hobbies", sa.Text()),
        sa.Column("budget_acknowledged", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("shipping_address", sa.Text()),
        sa.Column("country", sa.String(80)),
        sa.Column("organizer_wishlist_authorized", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("group_id", "user_id", name="uq_group_user"),
    )
    op.create_table(
        "wishlists",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("group_id", sa.String(36), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("participant_id", sa.String(36), sa.ForeignKey("group_participants.id"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("product_url", sa.String(1000)),
        sa.Column("image_url", sa.String(1000)),
        sa.Column("estimated_price", sa.Numeric(10, 2)),
        sa.Column("priority", sa.String(20), nullable=False),
        sa.Column("category", sa.String(40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "assignment_exclusions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("group_id", sa.String(36), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("participant_id", sa.String(36), sa.ForeignKey("group_participants.id"), nullable=False),
        sa.Column("excluded_participant_id", sa.String(36), sa.ForeignKey("group_participants.id"), nullable=False),
        sa.Column("reason", sa.String(255)),
        sa.UniqueConstraint("group_id", "participant_id", "excluded_participant_id", name="uq_exclusion_pair"),
    )
    op.create_table(
        "secret_santa_assignments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("group_id", sa.String(36), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("giver_participant_id", sa.String(36), sa.ForeignKey("group_participants.id"), nullable=False),
        sa.Column("receiver_participant_id", sa.String(36), sa.ForeignKey("group_participants.id"), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("group_id", "giver_participant_id", name="uq_assignment_giver"),
        sa.UniqueConstraint("group_id", "receiver_participant_id", name="uq_assignment_receiver"),
    )
    op.create_table(
        "gift_tracking",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("group_id", sa.String(36), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("assignment_id", sa.String(36), sa.ForeignKey("secret_santa_assignments.id"), nullable=False, unique=True),
        sa.Column("gift_status", sa.String(40), nullable=False),
        sa.Column("gift_description", sa.Text()),
        sa.Column("tracking_reference", sa.String(120)),
        sa.Column("photo_url", sa.String(1000)),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("group_id", sa.String(36), sa.ForeignKey("groups.id")),
        sa.Column("notification_type", sa.String(40), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("deep_link", sa.String(255)),
        sa.Column("read_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "group_invitations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("group_id", sa.String(36), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("invitation_email", sa.String(255)),
        sa.Column("invitation_code", sa.String(180), nullable=False, unique=True),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("group_id", sa.String(36), sa.ForeignKey("groups.id")),
        sa.Column("actor_user_id", sa.String(36), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("details", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "email_verification_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "group_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("group_id", sa.String(36), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("author_user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_groups_invite_code", "groups", ["invite_code"])
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])


def downgrade() -> None:
    for table in [
        "group_messages",
        "refresh_tokens",
        "password_reset_tokens",
        "email_verification_tokens",
        "audit_logs",
        "group_invitations",
        "notifications",
        "gift_tracking",
        "secret_santa_assignments",
        "assignment_exclusions",
        "wishlists",
        "group_participants",
        "groups",
        "users",
    ]:
        op.drop_table(table)
