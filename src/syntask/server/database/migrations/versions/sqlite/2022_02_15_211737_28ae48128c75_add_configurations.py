"""Add the configurations table.

Revision ID: 28ae48128c75
Revises: 7c91cb86dc4e
Create Date: 2022-02-17 21:17:37.538086

"""

import sqlalchemy as sa
from alembic import op

import syntask

# revision identifiers, used by Alembic.
revision = "28ae48128c75"
down_revision = "7c91cb86dc4e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "configuration",
        sa.Column(
            "id",
            syntask.server.utilities.database.UUID(),
            server_default=sa.text(
                "(\n    (\n        lower(hex(randomblob(4))) \n        || '-' \n       "
                " || lower(hex(randomblob(2))) \n        || '-4' \n        ||"
                " substr(lower(hex(randomblob(2))),2) \n        || '-' \n        ||"
                " substr('89ab',abs(random()) % 4 + 1, 1) \n        ||"
                " substr(lower(hex(randomblob(2))),2) \n        || '-' \n        ||"
                " lower(hex(randomblob(6)))\n    )\n    )"
            ),
            nullable=False,
        ),
        sa.Column(
            "created",
            syntask.server.utilities.database.Timestamp(timezone=True),
            server_default=sa.text("(strftime('%Y-%m-%d %H:%M:%f000', 'now'))"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            syntask.server.utilities.database.Timestamp(timezone=True),
            server_default=sa.text("(strftime('%Y-%m-%d %H:%M:%f000', 'now'))"),
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
