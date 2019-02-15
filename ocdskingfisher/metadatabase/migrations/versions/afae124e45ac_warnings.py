"""warnings

Revision ID: afae124e45ac
Revises: 647180c51888
Create Date: 2018-07-10 13:58:31.951170

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afae124e45ac'
down_revision = '647180c51888'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("filestatus",
                  sa.Column('fetch_warnings', sa.Text, nullable=True)
                  )


def downgrade():
    op.drop_column("filestatus", 'fetch_warnings')
