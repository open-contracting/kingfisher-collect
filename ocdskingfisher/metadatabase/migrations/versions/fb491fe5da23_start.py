"""start

Revision ID: fb491fe5da23
Revises:
Create Date: 2018-06-05 13:31:04.271714

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb491fe5da23'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('session',
                    sa.Column('publisher_name', sa.Text),
                    sa.Column('data_version', sa.Text),
                    sa.Column('base_url', sa.Text),
                    sa.Column('sample', sa.Boolean),
                    sa.Column('session_start_datetime', sa.DateTime),

                    sa.Column('gather_start_datetime', sa.DateTime, nullable=True),
                    sa.Column('gather_finished_datetime', sa.DateTime, nullable=True),
                    sa.Column('gather_errors', sa.Text, nullable=True),
                    sa.Column('gather_stacktrace', sa.Text, nullable=True),
                    sa.Column('gather_success', sa.Boolean, nullable=False, default=False),

                    sa.Column('fetch_start_datetime', sa.DateTime, nullable=True),
                    sa.Column('fetch_finished_datetime', sa.DateTime, nullable=True),
                    sa.Column('fetch_success', sa.Boolean, nullable=False, default=False),
                    )

    op.create_table('filestatus',
                    sa.Column('filename', sa.Text, primary_key=True),
                    sa.Column('url', sa.Text, nullable=False),
                    sa.Column('data_type', sa.Text, nullable=False),
                    sa.Column('encoding', sa.Text, nullable=False, default='utf-8'),

                    sa.Column('fetch_start_datetime', sa.DateTime, nullable=True),
                    sa.Column('fetch_finished_datetime', sa.DateTime, nullable=True),
                    sa.Column('fetch_errors', sa.Text, nullable=True),
                    sa.Column('fetch_success', sa.Boolean, nullable=False, default=False),
                    )


def downgrade():
    op.drop_table('filestatus')
    op.drop_table('session')
