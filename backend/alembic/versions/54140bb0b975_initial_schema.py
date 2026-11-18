"""initial schema

Revision ID: 54140bb0b975
Revises: 
Create Date: 2026-11-18 09:15:34.042248

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '54140bb0b975'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('companies',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
        sa.Index('ix_companies_slug', 'slug'),
    )

    op.create_table('users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_users_email', 'email', unique=True),
    )

    op.create_table('inventory_items',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('company_id', sa.Uuid(), nullable=True),
        sa.Column('sku', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('quantity_on_hand', sa.Integer(), nullable=False),
        sa.Column('unit_cost', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('reorder_level', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'sku', name='uq_company_sku'),
        sa.CheckConstraint('quantity_on_hand >= 0', name='ck_qty_positive'),
        sa.CheckConstraint('reorder_level >= 0', name='ck_reorder_positive'),
        sa.Index('ix_inventory_items_sku', 'sku'),
    )

    op.create_table('reconciliations',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('company_id', sa.Uuid(), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('source_file_name', sa.String(length=500), nullable=True),
        sa.Column('source_data', sa.JSON(), nullable=True),
        sa.Column('total_items', sa.Integer(), nullable=False),
        sa.Column('matched_items', sa.Integer(), nullable=False),
        sa.Column('discrepancies_found', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('discrepancies',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('reconciliation_id', sa.Uuid(), nullable=True),
        sa.Column('company_id', sa.Uuid(), nullable=True),
        sa.Column('inventory_item_id', sa.Uuid(), nullable=True),
        sa.Column('item_name', sa.String(length=500), nullable=False),
        sa.Column('item_sku', sa.String(length=100), nullable=True),
        sa.Column('system_quantity', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('source_quantity', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('quantity_difference', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('system_cost', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('source_cost', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('cost_difference', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('discrepancy_type', sa.String(length=30), nullable=False),
        sa.Column('severity', sa.String(length=10), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('resolved', sa.Boolean(), nullable=True),
        sa.Column('resolved_at', sa.String(length=50), nullable=True),
        sa.Column('resolved_by', sa.Uuid(), nullable=True),
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inventory_item_id'], ['inventory_items.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['reconciliation_id'], ['reconciliations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('discrepancies')
    op.drop_table('reconciliations')
    op.drop_table('inventory_items')
    op.drop_table('users')
    op.drop_table('companies')
