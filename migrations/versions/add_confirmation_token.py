"""Add confirmation_token to Order model for IDOR protection

Revision ID: a1b2c3d4e5f6
Revises: 93905323bbfc
Create Date: 2025-10-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import secrets


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '93905323bbfc'
branch_labels = None
depends_on = None


def upgrade():
    # Add confirmation_token column
    op.add_column('orders', sa.Column('confirmation_token', sa.String(length=64), nullable=True))
    op.create_unique_constraint('uq_orders_confirmation_token', 'orders', ['confirmation_token'])

    # Generate tokens for existing orders
    # This ensures existing orders get unique tokens when migration runs
    connection = op.get_bind()
    results = connection.execute(sa.text("SELECT id FROM orders WHERE confirmation_token IS NULL"))

    for row in results:
        token = secrets.token_urlsafe(32)
        connection.execute(
            sa.text("UPDATE orders SET confirmation_token = :token WHERE id = :id"),
            {"token": token, "id": row[0]}
        )


def downgrade():
    # Remove the column if we need to rollback
    op.drop_constraint('uq_orders_confirmation_token', 'orders', type_='unique')
    op.drop_column('orders', 'confirmation_token')
