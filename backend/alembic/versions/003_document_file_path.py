"""Add documents.file_path so a document delete can locate and remove the
underlying stored file (previously only the original display filename was
persisted, not the actual uploads/<uuid><ext> path it was saved under).

Revision ID: 003
Revises: 002
"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("file_path", sa.String(1000), nullable=True))


def downgrade() -> None:
    op.drop_column("documents", "file_path")
