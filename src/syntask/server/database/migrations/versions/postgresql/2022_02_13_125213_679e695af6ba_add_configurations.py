"""Add the configurations table.

Revision ID: 679e695af6ba
Revises: 5bff7878e700
Create Date: 2022-02-17 21:17:27.832400

"""

import sqlalchemy as sa
from alembic import op

import syntask

# revision identifiers, used by Alembic.
revision = "679e695af6ba"
down_revision = "5bff7878e700"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "configuration",
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
        sa.Column("key", sa.String(), nullable=False),
        sa.Column(
            "value",
            syntask.server.utilities.database.JSON(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_configuration")),
        sa.UniqueConstraint("key", name=op.f("uq_configuration__key")),
    )
    op.create_index(
        op.f("ix_configuration__key"), "configuration", ["key"], unique=False
    )
    op.create_index(
        op.f("ix_configuration__updated"), "configuration", ["updated"], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_configuration__updated"), table_name="configuration")
    op.drop_index(op.f("ix_configuration__key"), table_name="configuration")
    op.drop_table("configuration")
    # ### end Alembic commands ###
