"""State data migration cleanup

Revision ID: 2882cd2df466
Revises: 2882cd2df465
Create Date: 2023-01-26 04:55:02.358638

"""

import sqlalchemy as sa
from alembic import op

import syntask

# revision identifiers, used by Alembic.
revision = "2882cd2df466"
down_revision = "2882cd2df465"
branch_labels = None
depends_on = None


def upgrade():
    # drop state id columns after data migration
    with op.batch_alter_table("artifact", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_artifact__task_run_state_id"))
        batch_op.drop_column("task_run_state_id")
        batch_op.drop_index(batch_op.f("ix_artifact__flow_run_state_id"))
        batch_op.drop_column("flow_run_state_id")

    with op.batch_alter_table("flow_run_state", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_flow_run_state__has_data"))
        batch_op.drop_column("has_data")

    with op.batch_alter_table("task_run_state", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_task_run_state__has_data"))
        batch_op.drop_column("has_data")


def downgrade():
    with op.batch_alter_table("artifact", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "flow_run_state_id",
                syntask.server.utilities.database.UUID(),
                nullable=True,
            ),
        )
        batch_op.create_index(
            batch_op.f("ix_artifact__flow_run_state_id"),
            ["flow_run_state_id"],
            unique=False,
        )
        batch_op.add_column(
            sa.Column(
                "task_run_state_id",
                syntask.server.utilities.database.UUID(),
                nullable=True,
            ),
        )
        batch_op.create_index(
            batch_op.f("ix_artifact__task_run_state_id"),
            ["task_run_state_id"],
            unique=False,
        )

    with op.batch_alter_table("flow_run_state", schema=None) as batch_op:
        batch_op.add_column(sa.Column("has_data", sa.Boolean))
        batch_op.create_index(
            batch_op.f("ix_flow_run_state__has_data"),
            ["has_data"],
            unique=False,
        )

    with op.batch_alter_table("task_run_state", schema=None) as batch_op:
        batch_op.add_column(sa.Column("has_data", sa.Boolean))
        batch_op.create_index(
            batch_op.f("ix_task_run_state__has_data"),
            ["has_data"],
            unique=False,
        )
