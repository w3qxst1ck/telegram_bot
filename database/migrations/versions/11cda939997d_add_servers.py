"""add_servers

Revision ID: 11cda939997d
Revises: 1f26abe9b579
Create Date: 2025-02-24 18:32:26.450827

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "11cda939997d"
down_revision: Union[str, None] = "1f26abe9b579"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "servers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("region", sa.String(), nullable=False),
        sa.Column("api_url", sa.String(), nullable=False),
        sa.Column("domain", sa.String(), nullable=False),
        sa.Column("inbound_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.add_column("keys", sa.Column("server_id", sa.Integer(), nullable=False))
    op.create_unique_constraint(None, "keys", ["connection_id"])
    op.create_foreign_key(
        None, "keys", "servers", ["server_id"], ["id"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "keys", type_="foreignkey")
    op.drop_constraint(None, "keys", type_="unique")
    op.drop_column("keys", "server_id")
    op.drop_table("servers")
    # ### end Alembic commands ###
