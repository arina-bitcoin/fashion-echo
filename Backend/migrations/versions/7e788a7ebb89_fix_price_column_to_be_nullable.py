"""Fix price column to be nullable

Revision ID: 7e788a7ebb89
Revises: f439a75da403
Create Date: 2025-12-04 21:15:17.580419

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '7e788a7ebb89'
down_revision = 'f439a75da403'  # ВАЖНО: укажите предыдущую миграцию
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Для SQLite нужно пересоздать таблицу
    # 1. Создать временную таблицу с правильной схемой
    op.create_table(
        'ads_temp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=True),  # nullable=True
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('main_category', sa.String(length=20), nullable=True),
        sa.Column('sub_category', sa.String(length=20), nullable=True),
        sa.Column('season', sa.String(length=20), nullable=True),
        sa.Column('condition', sa.String(length=20), nullable=True),
        sa.Column('size', sa.String(length=50), nullable=True),
        sa.Column('colors', sa.JSON(), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('brand', sa.String(length=100), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('favorite_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 2. Скопировать данные из старой таблицы
    op.execute('''
        INSERT INTO ads_temp (id, title, description, price, type, status, main_category, 
                             sub_category, season, condition, size, colors, tags, brand,
                             view_count, favorite_count, user_id, created_at, updated_at)
        SELECT id, title, description, price, type, status, main_category,
               sub_category, season, condition, size, colors, tags, brand,
               view_count, favorite_count, user_id, created_at, updated_at
        FROM ads
    ''')
    
    # 3. Удалить старую таблицу
    op.drop_table('ads')
    
    # 4. Переименовать временную таблицу
    op.rename_table('ads_temp', 'ads')


def downgrade() -> None:
    # Обратное преобразование
    op.create_table(
        'ads_temp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),  # nullable=False
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('main_category', sa.String(length=20), nullable=True),
        sa.Column('sub_category', sa.String(length=20), nullable=True),
        sa.Column('season', sa.String(length=20), nullable=True),
        sa.Column('condition', sa.String(length=20), nullable=True),
        sa.Column('size', sa.String(length=50), nullable=True),
        sa.Column('colors', sa.JSON(), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('brand', sa.String(length=100), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('favorite_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Копируем только записи где price не NULL
    op.execute('''
        INSERT INTO ads_temp (id, title, description, price, type, status, main_category, 
                             sub_category, season, condition, size, colors, tags, brand,
                             view_count, favorite_count, user_id, created_at, updated_at)
        SELECT id, title, description, COALESCE(price, 0.0), type, status, main_category,
               sub_category, season, condition, size, colors, tags, brand,
               view_count, favorite_count, user_id, created_at, updated_at
        FROM ads
    ''')
    
    op.drop_table('ads')
    op.rename_table('ads_temp', 'ads')