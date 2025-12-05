import asyncio
import sys
from pathlib import Path
import traceback

# Добавляем корень проекта в sys.path (как у тебя было)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from Backend.app.core.database import engine

async def add_brand_column():
    """Добавить колонку brand в таблицу ads"""
    async with engine.begin() as conn:
        # Проверяем, есть ли уже колонка brand
        result = await conn.execute(
            text("PRAGMA table_info(ads)")
        )
        columns = [row[1] for row in result]
        
        if 'brand' not in columns:
            print("Добавляем колонку brand в таблицу ads...")
            await conn.execute(
                text("ALTER TABLE ads ADD COLUMN brand VARCHAR(100)")
            )
            print("Колонка brand успешно добавлена!")
        else:
            print("Колонка brand уже существует")

if __name__ == "__main__":
    asyncio.run(add_brand_column())