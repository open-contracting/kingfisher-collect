"""priority

Revision ID: 647180c51888
Revises: fb491fe5da23
Create Date: 2018-07-05 14:10:04.492412

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '647180c51888'
down_revision = 'fb491fe5da23'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("filestatus",
                  sa.Column('priority', sa.Integer, nullable=False, server_default='1')
                  )


def downgrade():
    op.drop_column("filestatus", 'priority')
