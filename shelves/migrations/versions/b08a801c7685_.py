"""empty message

Revision ID: b08a801c7685
Revises: 0ac6df6bb852
Create Date: 2024-07-24 16:07:40.105475

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b08a801c7685'
down_revision = '0ac6df6bb852'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('burrowed', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.drop_column('burrowed')

    # ### end Alembic commands ###