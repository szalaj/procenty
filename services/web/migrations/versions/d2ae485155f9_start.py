"""start

Revision ID: d2ae485155f9
Revises: 
Create Date: 2023-12-05 23:11:17.012028

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2ae485155f9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dom',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('wartosc', sa.Numeric(), nullable=False),
    sa.Column('data_zakupu', sa.String(length=10), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('inflacjamm',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('miesiac', sa.DateTime(), nullable=False),
    sa.Column('wartosc', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('miesiac')
    )
    op.create_table('kredyt',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uzytkownik', sa.String(), nullable=False),
    sa.Column('data_uruchomienia', sa.DateTime(), nullable=False),
    sa.Column('data_umowy', sa.DateTime(), nullable=True),
    sa.Column('wartosc', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('okresy', sa.Integer(), nullable=False),
    sa.Column('marza', sa.Float(), nullable=False),
    sa.Column('rodzaj_wiboru', sa.String(), nullable=False),
    sa.Column('rodzaj_rat', sa.String(), nullable=False),
    sa.Column('ubezpieczenie_pomostowe_do', sa.DateTime(), nullable=True),
    sa.Column('ubezpieczenie_pomostowe_stopa', sa.Numeric(precision=14, scale=2), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=1000), nullable=True),
    sa.Column('password', sa.String(length=100), nullable=True),
    sa.Column('liczba_logowan', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('wibor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rodzaj', sa.String(), nullable=False),
    sa.Column('data', sa.DateTime(), nullable=False),
    sa.Column('wartosc', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('zapytanie',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user', sa.String(length=1000), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dni_splaty',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('kredyt_id', sa.Integer(), nullable=False),
    sa.Column('dzien_splaty', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['kredyt_id'], ['kredyt.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('nadplata',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('kredyt_id', sa.Integer(), nullable=False),
    sa.Column('data_nadplaty', sa.DateTime(), nullable=False),
    sa.Column('wartosc', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['kredyt_id'], ['kredyt.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('wakacje',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('kredyt_id', sa.Integer(), nullable=False),
    sa.Column('miesiac', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['kredyt_id'], ['kredyt.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wakacje')
    op.drop_table('nadplata')
    op.drop_table('dni_splaty')
    op.drop_table('zapytanie')
    op.drop_table('wibor')
    op.drop_table('user')
    op.drop_table('kredyt')
    op.drop_table('inflacjamm')
    op.drop_table('dom')
    # ### end Alembic commands ###
