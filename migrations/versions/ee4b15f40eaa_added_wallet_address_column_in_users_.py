"""added wallet_address column in Users table

Revision ID: ee4b15f40eaa
Revises: c25b9c0afa5c
Create Date: 2023-04-02 02:59:03.466068

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee4b15f40eaa'
down_revision = 'c25b9c0afa5c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('wallet_address', sa.String(length=200), nullable=False))
        batch_op.drop_constraint('users_phone_key', type_='unique')
        batch_op.create_unique_constraint(None, ['wallet_address'])
        batch_op.drop_column('phone')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone', sa.VARCHAR(length=80), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.create_unique_constraint('users_phone_key', ['phone'])
        batch_op.drop_column('wallet_address')

    # ### end Alembic commands ###
