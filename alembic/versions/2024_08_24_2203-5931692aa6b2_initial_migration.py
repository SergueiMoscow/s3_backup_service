"""initial migration

Revision ID: 5931692aa6b2
Revises: 
Create Date: 2024-08-24 22:03:02.343120

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5931692aa6b2"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "s3_storages",
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.Column("url", sa.String(length=255), nullable=False),
        sa.Column("access_key", sa.String(length=255), nullable=False),
        sa.Column("secret_key", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_s3storage_name", "s3_storages", ["name"], unique=False
    )
    op.create_index(
        op.f("ix_s3_storages_name"), "s3_storages", ["name"], unique=False
    )
    op.create_table(
        "backup_file",
        sa.Column("storage_id", sa.Integer(), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("file_time", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["storage_id"], ["s3_storages.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_storage_file_name",
        "backup_file",
        ["storage_id", "file_name"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_storage_file_name", table_name="backup_file")
    op.drop_table("backup_file")
    op.drop_index(op.f("ix_s3_storages_name"), table_name="s3_storages")
    op.drop_index("idx_s3storage_name", table_name="s3_storages")
    op.drop_table("s3_storages")
