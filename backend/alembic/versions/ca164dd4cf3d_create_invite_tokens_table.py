"""create_invite_tokens_table

Revision ID: ca164dd4cf3d
Revises: dd5ee5d283dd
Create Date: 2026-07-11 21:00:57.380118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca164dd4cf3d'
down_revision: Union[str, Sequence[str], None] = 'dd5ee5d283dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('invite_tokens',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('is_used', sa.Boolean(), nullable=False),
    sa.Column('used_by_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['used_by_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invite_tokens_token'), 'invite_tokens', ['token'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_invite_tokens_token'), table_name='invite_tokens')
    op.drop_table('invite_tokens')
