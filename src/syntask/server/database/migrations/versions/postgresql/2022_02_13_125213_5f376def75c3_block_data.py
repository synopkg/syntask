"""Add the block data table.

Revision ID: 5f376def75c3
Revises: 25f4b90a7a42
Create Date: 2022-02-13 12:52:13.264435

"""

import sqlalchemy as sa
from alembic import op

import syntask

# revision identifiers, used by Alembic.
revision = "5f376def75c3"
down_revision = "25f4b90a7a42"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "block_data",
        sa.Column(
            "id",
            syntask.server.utilities.database.UUID(),
            server_default=sa.text("(GEN_RANDOM_UUID())"),
            nullable=False,
        ),
        sa.Column(
            "created",
            syntask.server.utilities.database.Timestamp(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            syntask.server.utilities.database.Timestamp(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("blockref", sa.String(), nullable=False),
        sa.Column(
            "data",
            syntask.server.utilities.database.JSON(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_block_data")),
    )
    op.create_index(op.f("ix_block_data__name"), "block_data", ["name"], unique=True)
    op.create_index(
        op.f("ix_block_data__updated"), "block_data", ["updated"], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_block_data__updated"), table_name="block_data")
    op.drop_index(op.f("ix_block_data__name"), table_name="block_data")
    op.drop_table("block_data")
    # ### end Alembic commands ###
