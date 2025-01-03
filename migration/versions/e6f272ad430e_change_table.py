"""Change table

Revision ID: e6f272ad430e
Revises: e66ed0c15f45
Create Date: 2025-01-02 11:15:52.970772

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6f272ad430e'
down_revision: Union[str, None] = 'e66ed0c15f45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('posts', 'sauna_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=255),
               existing_nullable=False)
    op.alter_column('saunas', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=255),
               existing_nullable=False,
               existing_server_default=sa.text("nextval('saunas_id_seq'::regclass)"))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('saunas', 'id',
               existing_type=sa.String(length=255),
               type_=sa.INTEGER(),
               existing_nullable=False,
               existing_server_default=sa.text("nextval('saunas_id_seq'::regclass)"))
    op.alter_column('posts', 'sauna_id',
               existing_type=sa.String(length=255),
               type_=sa.INTEGER(),
               existing_nullable=False)
    # ### end Alembic commands ###
