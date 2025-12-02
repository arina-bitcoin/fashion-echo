# Backend/app/core/initial_data.py

import os
import json
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from Backend.app.models.secondhand import Secondhand


def backup_secondhands(db: Session, backup_dir: str = "db/backups") -> str:
    """
    Бэкап секондхендов в JSON-файл.
    Возвращает путь к созданному файлу.
    """
    os.makedirs(backup_dir, exist_ok=True)

    secondhands: List[Secondhand] = db.query(Secondhand).all()

    data = []
    for sh in secondhands:
        data.append(
            {
                "id": sh.id,
                "name": sh.name,
                "address": sh.address,
                "city": "Москва",
                "latitude": sh.latitude,
                "longitude": sh.longitude,
                "phone": sh.phone,
                "email": sh.email,
                "website": sh.website,
                "description": sh.description,
                "opening_hours": sh.opening_hours,
                "is_active": sh.is_active,
            }
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"secondhands_{timestamp}.json")

    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"📦 Бэкап секондхендов сохранён в {backup_path}")
    return backup_path


def initialize_secondhands(db: Session):
    """
    Инициализация таблицы секондхендов тестовыми данными.
    Если в таблице уже есть записи, ничего не делает.
    """
    existing_count = db.query(Secondhand).count()
    if existing_count > 0:
        print(f"ℹ️ В таблице secondhands уже есть данные ({existing_count} записей), инициализация пропущена.")
        return

    print("🚀 Инициализация тестовых данных для секондхендов...")

    # ВАЖНО: поля должны соответствовать МОДЕЛИ Secondhand, а не схеме!
    secondhands_data = [
        {
            "name": "Secondhand 'Fashion Recycle'",
            "address": "Москва, ул. Тверская, 10",
            "city": "Москва",
            "latitude": 55.7570,
            "longitude": 37.6150,
            "phone": "+7 495 123-45-67",
            "email": "info@fashion-recycle.ru",
            "website": "https://fashion-recycle.ru",
            "description": "Экологичный секондхенд с качественной одеждой.",
            "opening_hours": {
                "mon": "10:00-20:00",
                "tue": "10:00-20:00",
                "wed": "10:00-20:00",
                "thu": "10:00-20:00",
                "fri": "10:00-21:00",
                "sat": "11:00-19:00",
                "sun": "11:00-18:00",
            },
            "is_active": True,
        },
        {
            "name": "Второе Дыхание",
            "address": "Москва, ул. Арбат, 25",
            "city": "Москва",
            "latitude": 55.7495,
            "longitude": 37.5920,
            "phone": "+7 495 765-43-21",
            "email": "info@vtoroe-dyhanie.ru",
            "website": "https://vtoroe-dyhanie.ru",
            "description": "Секондхенд с упором на винтаж и редкие находки.",
            "opening_hours": {
                "mon": "11:00-20:00",
                "tue": "11:00-20:00",
                "wed": "11:00-20:00",
                "thu": "11:00-20:00",
                "fri": "11:00-21:00",
                "sat": "11:00-21:00",
                "sun": "11:00-18:00",
            },
            "is_active": True,
        },
        {
            "name": "Green Wardrobe",
            "address": "Санкт-Петербург, Невский проспект, 100",
            "city": "Москва",
            "latitude": 59.9311,
            "longitude": 30.3609,
            "phone": "+7 812 111-22-33",
            "email": "hello@greenwardrobe.ru",
            "website": None,
            "description": "Секондхенд с акцентом на устойчивую моду и переработку.",
            "opening_hours": {
                "mon": "10:00-19:00",
                "tue": "10:00-19:00",
                "wed": "10:00-19:00",
                "thu": "10:00-19:00",
                "fri": "10:00-19:00",
                "sat": "11:00-18:00",
                "sun": "выходной",
            },
            "is_active": True,
        },
        {
            "name": "Retro Chic",
            "address": "Санкт-Петербург, Литейный проспект, 45",
            "city": "Москва",
            "latitude": 59.9390,
            "longitude": 30.3490,
            "phone": None,
            "email": None,
            "website": None,
            "description": "Небольшой магазин с ретро-платьями и аксессуарами.",
            "opening_hours": {
                "mon": "12:00-20:00",
                "tue": "12:00-20:00",
                "wed": "12:00-20:00",
                "thu": "12:00-20:00",
                "fri": "12:00-21:00",
                "sat": "12:00-21:00",
                "sun": "12:00-18:00",
            },
            "is_active": True,
        },
        {
            "name": "Eco Closet",
            "address": "Казань, ул. Баумана, 15",
            "city": "Москва",
            "latitude": 55.7963,
            "longitude": 49.1088,
            "phone": "+7 843 555-66-77",
            "email": "contact@ecocloset.ru",
            "website": "https://ecocloset.ru",
            "description": "Секондхенд с современной одеждой и системой обмена вещей.",
            "opening_hours": {
                "mon": "10:00-20:00",
                "tue": "10:00-20:00",
                "wed": "10:00-20:00",
                "thu": "10:00-20:00",
                "fri": "10:00-20:00",
                "sat": "11:00-19:00",
                "sun": "11:00-18:00",
            },
            "is_active": True,
        },
    ]

    for data in secondhands_data:
        db.add(Secondhand(**data))

    db.commit()

    print(f"✅ Инициализация завершена: добавлено {len(secondhands_data)} секондхендов.")
