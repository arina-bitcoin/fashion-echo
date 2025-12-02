# Backend/init_db.py

import os

from Backend.app.core.database import Base, engine, SessionLocal
from Backend.app.core.initial_data import initialize_secondhands


def init_database():
    print("🗃️ Создание таблиц в базе данных...")

    # создаём таблицы (если их ещё нет)
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы успешно созданы!")

    # проверяем наличие файла БД
    db_path = os.path.join("db", "fashion_eco.db")
    if os.path.exists(db_path):
        print(f"✅ Файл базы данных найден: {db_path}")
    else:
        print(f"⚠️ Файл БД не найден по пути: {db_path}")

    # инициализация тестовых данных
    db = SessionLocal()
    try:
        initialize_secondhands(db)
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
