"""Create new table

Revision ID: 485560def0c9
Revises: 
Create Date: 2024-12-24 14:25:09.452468

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '485560def0c9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass