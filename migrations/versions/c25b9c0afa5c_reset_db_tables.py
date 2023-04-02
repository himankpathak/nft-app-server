"""reset db tables

Revision ID: c25b9c0afa5c
Revises: 90f04ec523a2
Create Date: 2023-04-02 00:06:36.254495

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c25b9c0afa5c'
down_revision = '90f04ec523a2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('counter')
    op.drop_table('verify')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('verify',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('phone', sa.VARCHAR(length=80), autoincrement=False, nullable=False),
    sa.Column('otp', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='verify_pkey'),
    sa.UniqueConstraint('phone', name='verify_phone_key')
    )
    op.create_table('counter',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='counter_pkey')
    )
    # ### end Alembic commands ###