"""Adds block schema references and block document references

Revision ID: 2fe6fe6ca16e
Revises: 724e6dcc6b5d
Create Date: 2022-05-28 08:18:21.527986

"""

import sqlalchemy as sa
from alembic import op

import syntask
from syntask.blocks.core import Block

# revision identifiers, used by Alembic.
revision = "2fe6fe6ca16e"
down_revision = "724e6dcc6b5d"
branch_labels = None
depends_on = None

# Used to update titles of existing storage block schemas. Need to update titles to match
# what the client generates to ensure the same checksum is generated on client and server.
BLOCK_SCHEMA_TITLE_MAP = {
    "S3 Storage": "S3StorageBlock",
    "Temporary Local Storage": "TempStorageBlock",
    "Local Storage": "LocalStorageBlock",
    "Google Cloud Storage": "GoogleCloudStorageBlock",
    "Azure Blob Storage": "AzureBlobStorageBlock",
    "KV Server Storage": "KVServerStorageBlock",
    "File Storage": "FileStorageBlock",
}


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "block_schema_reference",
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
        sa.Column(
            "parent_block_schema_id",
            syntask.server.utilities.database.UUID(),
            nullable=False,
        ),
        sa.Column(
            "reference_block_schema_id",
            syntask.server.utilities.database.UUID(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["parent_block_schema_id"],
            ["block_schema.id"],
            name=op.f(
                "fk_block_schema_reference__parent_block_schema_id__block_schema"
            ),
            ondelete="cascade",
        ),
        sa.ForeignKeyConstraint(
            ["reference_block_schema_id"],
            ["block_schema.id"],
            name=op.f(
                "fk_block_schema_reference__reference_block_schema_id__block_schema"
            ),
            ondelete="cascade",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_block_schema_reference")),
    )
    op.create_index(
        op.f("ix_block_schema_reference__updated"),
        "block_schema_reference",
        ["updated"],
        unique=False,
    )
    op.create_table(
        "block_document_reference",
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
        sa.Column(
            "parent_block_document_id",
            syntask.server.utilities.database.UUID(),
            nullable=False,
        ),
        sa.Column(
            "reference_block_document_id",
            syntask.server.utilities.database.UUID(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["parent_block_document_id"],
            ["block_document.id"],
            name=op.f(
                "fk_block_document_reference__parent_block_document_id__block_document"
            ),
            ondelete="cascade",
        ),
        sa.ForeignKeyConstraint(
            ["reference_block_document_id"],
            ["block_document.id"],
            name=op.f(
                "fk_block_document_reference__reference_block_document_id__block_document"
            ),
            ondelete="cascade",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_block_document_reference")),
    )
    op.create_index(
        op.f("ix_block_document_reference__updated"),
        "block_document_reference",
        ["updated"],
        unique=False,
    )

    # Update existing schemas to account for block schema references
    connection = op.get_bind()
    meta_data = sa.MetaData()
    meta_data.reflect(connection)
    BLOCK_SCHEMA = meta_data.tables["block_schema"]
    BLOCK_TYPE = meta_data.tables["block_type"]

    block_schemas = connection.execute(
        sa.select(
            BLOCK_SCHEMA.c.id, BLOCK_SCHEMA.c.fields, BLOCK_SCHEMA.c.block_type_id
        )
    )

    for id, fields, block_type_id in block_schemas:
        block_type_result = connection.execute(
            sa.select(BLOCK_TYPE.c.name).where(BLOCK_TYPE.c.id == block_type_id)
        ).first()
        block_type_name = block_type_result[0]
        updated_fields = {
            **fields,
            "block_type_name": block_type_name,
            "block_schema_references": {},
        }
        updated_title = BLOCK_SCHEMA_TITLE_MAP.get(block_type_name)
        if updated_title is not None:
            updated_fields["title"] = updated_title
        updated_checksum = Block._calculate_schema_checksum(updated_fields)
        connection.execute(
            sa.update(BLOCK_SCHEMA)
            .where(BLOCK_SCHEMA.c.id == id)
            .values(fields=updated_fields, checksum=updated_checksum)
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_block_document_reference__updated"),
        table_name="block_document_reference",
    )
    op.drop_table("block_document_reference")
    op.drop_index(
        op.f("ix_block_schema_reference__updated"), table_name="block_schema_reference"
    )
    op.drop_table("block_schema_reference")
    # ### end Alembic commands ###
