"""empty message

Revision ID: f2ee8fc11d78
Revises:
Create Date: 2025-02-09 18:16:42.553305

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f2ee8fc11d78"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "subscriptions",
        sa.Column("tg_id", sa.String(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('utc-3', now())"),
            nullable=False,
        ),
        sa.Column("start_date", sa.DateTime(), nullable=True),
        sa.Column("expire_date", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("tg_id"),
    )
    op.create_table(
        "trial_subscriptions",
        sa.Column("tg_id", sa.String(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('utc-3', now())"),
            nullable=False,
        ),
        sa.Column(
            "expired_at",
            sa.DateTime(),
            server_default=sa.text(
                "TIMEZONE('utc-3', now() + interval '1 day')"
            ),
            nullable=False,
        ),
        sa.Column("is_used", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("tg_id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tg_id", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("firstname", sa.String(), nullable=True),
        sa.Column("lastname", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('utc-3', now())"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_tg_id"), "users", ["tg_id"], unique=True)
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("status", sa.Boolean(), nullable=False),
        sa.Column("user_tg_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_tg_id"], ["users.tg_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("payments")
    op.drop_index(op.f("ix_users_tg_id"), table_name="users")
    op.drop_table("users")
    op.drop_table("trial_subscriptions")
    op.drop_table("subscriptions")
    # ### end Alembic commands ###
