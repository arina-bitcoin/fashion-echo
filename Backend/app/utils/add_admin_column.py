import asyncio
import sys
from pathlib import Path

# Добавляем корень проекта в sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from sqlalchemy import text
from Backend.app.core.database import engine

async def add_is_admin_column():
    """Добавить колонку is_admin в таблицу users"""
    async with engine.begin() as conn:
        # Проверяем, есть ли уже колонка is_admin
        result = await conn.execute(
            text("PRAGMA table_info(users)")
        )
        columns = [row[1] for row in result]
        
        print("Существующие колонки в таблице users:", columns)
        
        if 'is_admin' not in columns:
            print("Добавляем колонку is_admin в таблицу users...")
            await conn.execute(
                text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
            )
            print("✅ Колонка is_admin успешно добавлена!")
        else:
            print("Колонка is_admin уже существует")

if __name__ == "__main__":
    asyncio.run(add_is_admin_column())