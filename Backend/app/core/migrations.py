import asyncio
from sqlalchemy import text
from Backend.app.core.database import engine

async def migrate_database():
    """Миграция базы данных для добавления новых полей"""
    async with engine.begin() as conn:
        # Проверяем существование колонок
        result = await conn.execute(text("PRAGMA table_info(ads)"))
        columns = [row[1] for row in result]
        
        print(f"Существующие колонки: {columns}")
        
        # Добавляем отсутствующие колонки (включая view_count и favorite_count)
        columns_to_add = [
            ('status', "TEXT DEFAULT 'active'"),
            ('main_category', 'TEXT'),
            ('sub_category', 'TEXT'),
            ('season', 'TEXT'),
            ('condition', 'TEXT'),
            ('size', 'TEXT'),
            ('colors', "TEXT DEFAULT '[]'"),
            ('tags', 'TEXT'),
            ('view_count', 'INTEGER DEFAULT 0'),      # ДОБАВЛЯЕМ перед пересозданием
            ('favorite_count', 'INTEGER DEFAULT 0'),  # ДОБАВЛЯЕМ перед пересозданием
            ('location', 'TEXT'),
            ('is_negotiable', 'BOOLEAN DEFAULT FALSE'),
        ]
        
        for column_name, column_type in columns_to_add:
            if column_name not in columns:
                print(f"Добавляем колонку {column_name}...")
                try:
                    await conn.execute(text(f"ALTER TABLE ads ADD COLUMN {column_name} {column_type}"))
                except Exception as e:
                    print(f"⚠️ Ошибка при добавлении колонки {column_name}: {e}")
        
        # Обновляем список колонок после добавления
        result = await conn.execute(text("PRAGMA table_info(ads)"))
        columns = [row[1] for row in result]
        print(f"Колонки после добавления: {columns}")
        
        # Удаляем старую колонку is_active если она существует
        if 'is_active' in columns:
            print("Удаляем старую колонку is_active...")
            # Сначала обновим существующие записи
            await conn.execute(text("UPDATE ads SET status = 'active' WHERE is_active = 1"))
            await conn.execute(text("UPDATE ads SET status = 'inactive' WHERE is_active = 0"))
            
            # Затем удалим колонку (SQLite не поддерживает DROP COLUMN напрямую)
            # Создадим временную таблицу с новой структурой
            await conn.execute(text("""
                CREATE TABLE ads_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    type TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    main_category TEXT,
                    sub_category TEXT,
                    season TEXT,
                    condition TEXT,
                    size TEXT,
                    colors TEXT DEFAULT '[]',
                    tags TEXT,
                    view_count INTEGER DEFAULT 0,
                    favorite_count INTEGER DEFAULT 0,
                    location TEXT,
                    is_negotiable BOOLEAN DEFAULT FALSE,
                    user_id INTEGER,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """))
            
            # Копируем данные - ВАЖНО: используем COALESCE для новых колонок
            await conn.execute(text("""
                INSERT INTO ads_new (
                    id, title, description, price, type, status,
                    main_category, sub_category, season, condition,
                    size, colors, tags, view_count, favorite_count,
                    location, is_negotiable, user_id, created_at, updated_at
                ) SELECT 
                    id, title, description, price, type, 
                    COALESCE(status, 'active') as status,
                    main_category, sub_category, season, condition,
                    size, COALESCE(colors, '[]') as colors,
                    tags, 
                    COALESCE(view_count, 0) as view_count,
                    COALESCE(favorite_count, 0) as favorite_count,
                    location, 
                    COALESCE(is_negotiable, FALSE) as is_negotiable,
                    user_id, created_at, updated_at
                FROM ads
            """))
            
            # Удаляем старую таблицу и переименовываем новую
            await conn.execute(text("DROP TABLE ads"))
            await conn.execute(text("ALTER TABLE ads_new RENAME TO ads"))
            
            print("✅ Таблица ads успешно обновлена")
        
        print("✅ Миграция базы данных завершена успешно!")

if __name__ == "__main__":
    asyncio.run(migrate_database())