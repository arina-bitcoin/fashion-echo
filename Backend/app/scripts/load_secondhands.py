import asyncio
import csv
import json
import sys
from pathlib import Path

# === Делаем, чтобы импорт Backend.* работал ===
# BASE_DIR -> корень проекта: .../PythonProject14/fashion-echo
BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BASE_DIR))

from Backend.app.core.database import async_session_maker, create_db_and_tables
from Backend.app.models.secondhand import Secondhand

# Путь к CSV-файлу
# Можешь оставить абсолютный путь, как у тебя:
CSV_PATH = Path(r"C:\Users\USER\Downloads\secondhend.csv")
# Или сделать относительный, если перенесёшь файл в проект, например:
# CSV_PATH = BASE_DIR / "File_storage" / "secondhend.csv"


async def main():
    # На всякий случай создаём таблицы, если их ещё нет
    await create_db_and_tables()

    async with async_session_maker() as session:
        with CSV_PATH.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0

            for row in reader:
                try:
                    lat = float(row["latitude"]) if row.get("latitude") else None
                    lng = float(row["longitude"]) if row.get("longitude") else None

                    opening_hours_raw = row.get("opening_hours") or None
                    opening_hours = None
                    if opening_hours_raw:
                        # opening_hours хранится в CSV как JSON-строка
                        opening_hours = json.loads(opening_hours_raw)

                    secondhand = Secondhand(
                        name=row["name"],
                        address=row["address"],
                        city=row["city"],
                        phone=row.get("phone") or None,
                        email=row.get("email") or None,
                        website=row.get("website") or None,
                        description=row.get("description") or None,
                        latitude=lat,
                        longitude=lng,
                        opening_hours=opening_hours,
                        is_active=True,
                    )

                    session.add(secondhand)
                    count += 1

                except Exception as e:
                    print("❌ Ошибка в строке:", row)
                    print("   Причина:", e)

        await session.commit()
        print(f"✅ Импорт завершён, добавлено секондов: {count}")


if __name__ == "__main__":
    asyncio.run(main())
