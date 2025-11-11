"""Initial migration: create all tables

Revision ID: 20d8c95c0815
Revises: 
Create Date: 2025-11-11 15:08:28.747607

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20d8c95c0815'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - create all tables and indexes."""
    # Create firms table
    op.create_table(
        'firms',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('firm_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['firm_id'], ['firms.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_users_firm_id', 'users', ['firm_id'])
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('firm_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('s3_key', sa.String(length=512), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['firm_id'], ['firms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_documents_firm_id', 'documents', ['firm_id'])
    op.create_index('idx_documents_uploaded_at', 'documents', ['uploaded_at'])
    op.create_index('ix_documents_s3_key', 'documents', ['s3_key'], unique=True)

    # Create letter_templates table
    op.create_table(
        'letter_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('firm_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('letterhead_text', sa.Text(), nullable=True),
        sa.Column('opening_paragraph', sa.Text(), nullable=True),
        sa.Column('closing_paragraph', sa.Text(), nullable=True),
        sa.Column('sections', postgresql.JSONB(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['firm_id'], ['firms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_letter_templates_firm_id', 'letter_templates', ['firm_id'])

    # Create generated_letters table
    op.create_table(
        'generated_letters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('firm_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('docx_s3_key', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['firm_id'], ['firms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['template_id'], ['letter_templates.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_letters_firm_id', 'generated_letters', ['firm_id'])
    op.create_index('idx_letters_created_at', 'generated_letters', ['created_at'])
    op.create_index('idx_letters_status', 'generated_letters', ['status'])

    # Create letter_source_documents junction table
    op.create_table(
        'letter_source_documents',
        sa.Column('letter_id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.ForeignKeyConstraint(['letter_id'], ['generated_letters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    """Downgrade schema - drop all tables."""
    op.drop_table('letter_source_documents')
    op.drop_index('idx_letters_status', table_name='generated_letters')
    op.drop_index('idx_letters_created_at', table_name='generated_letters')
    op.drop_index('idx_letters_firm_id', table_name='generated_letters')
    op.drop_table('generated_letters')
    op.drop_index('ix_letter_templates_firm_id', table_name='letter_templates')
    op.drop_table('letter_templates')
    op.drop_index('ix_documents_s3_key', table_name='documents')
    op.drop_index('idx_documents_uploaded_at', table_name='documents')
    op.drop_index('idx_documents_firm_id', table_name='documents')
    op.drop_table('documents')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_firm_id', table_name='users')
    op.drop_table('users')
    op.drop_table('firms')
