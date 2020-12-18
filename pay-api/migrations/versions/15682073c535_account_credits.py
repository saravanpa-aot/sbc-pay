"""account_credits

Revision ID: 15682073c535
Revises: 331c2cdb0b94
Create Date: 2020-12-16 12:25:50.774792

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '15682073c535'
down_revision = '331c2cdb0b94'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('credits',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('cfs_identifier', sa.String(length=50), nullable=True),
                    sa.Column('is_credit_memo', sa.Boolean(), nullable=True),
                    sa.Column('amount', sa.Float(), nullable=False),
                    sa.Column('remaining_amount', sa.Float(), nullable=False),
                    sa.Column('account_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['account_id'], ['payment_account.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_credits_account_id'), 'credits', ['account_id'], unique=False)
    op.create_index(op.f('ix_credits_cfs_identifier'), 'credits', ['cfs_identifier'], unique=False)
    op.drop_column('payment', 'created_on')
    op.drop_column('payment_account', 'running_balance')
    op.drop_column('payment_account_version', 'running_balance')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payment_account_version',
                  sa.Column('running_balance', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False,
                            nullable=True))
    op.add_column('payment_account',
                  sa.Column('running_balance', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False,
                            nullable=True))
    op.add_column('payment', sa.Column('created_on', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))

    op.drop_index(op.f('ix_credits_cfs_identifier'), table_name='credits')
    op.drop_index(op.f('ix_credits_account_id'), table_name='credits')
    op.drop_table('credits')
    # ### end Alembic commands ###