"""Changing table

Revision ID: 9978dd9aab3e
Revises: d2e9d34cca29
Create Date: 2025-01-05 13:20:47.822726

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9978dd9aab3e'
down_revision: Union[str, None] = 'd2e9d34cca29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('posts', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('saunas', 'latitude',
               existing_type=sa.TEXT(),
               type_=sa.Float(),
               existing_nullable=False,
               postgresql_using="latitude::double precision")
    op.alter_column('saunas', 'longitude',
               existing_type=sa.TEXT(),
               type_=sa.Float(),
               existing_nullable=False,
               postgresql_using="longitude::double precision")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('saunas', 'longitude',
               existing_type=sa.Float(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('saunas', 'latitude',
               existing_type=sa.Float(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('posts', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    # ### end Alembic commands ###
