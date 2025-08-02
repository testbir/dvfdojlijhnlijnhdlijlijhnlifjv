"""Add link to banners and order to courses

Revision ID: c261e9fc7a41
Revises: a670d0b10fca
Create Date: 2025-07-04 17:32:06.947674
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c261e9fc7a41'
down_revision: Union[str, Sequence[str], None] = 'a670d0b10fca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('courses_course', sa.Column('order', sa.Integer(), nullable=True))
    op.add_column('homepage_banners', sa.Column('link', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('homepage_banners', 'link')
    op.drop_column('courses_course', 'order')
