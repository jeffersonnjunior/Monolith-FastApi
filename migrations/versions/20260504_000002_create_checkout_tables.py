"""create checkout tables

Revision ID: 20260504_000002
Revises: 20260428_000001
Create Date: 2026-05-04 15:45:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260504_000002"
down_revision: str | None = "20260428_000001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "payment_checkouts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("failure_reason", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payment_checkouts_idempotency_key", "payment_checkouts", ["idempotency_key"], unique=True)
    op.create_index("ix_payment_checkouts_user_id", "payment_checkouts", ["user_id"], unique=False)

    op.create_table(
        "user_balances",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("balance", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
    )


def downgrade() -> None:
    op.drop_table("user_balances")
    op.drop_index("ix_payment_checkouts_user_id", table_name="payment_checkouts")
    op.drop_index("ix_payment_checkouts_idempotency_key", table_name="payment_checkouts")
    op.drop_table("payment_checkouts")
