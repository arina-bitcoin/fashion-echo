"""
Скрипт для инициализации секондхендов в базе данных
"""
import sys
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Backend.app.core.initial_data import initialize_secondhands_sync

def init_secondhands():
    """Инициализация секондхендов"""
    try:
        # Находим путь к базе данных
        db_path = project_root / "Backend" / "database.db"
        if not db_path.exists():
            # Пробуем альтернативный путь
            db_path = project_root / "database.db"
        
        if not db_path.exists():
            print(f"❌ База данных не найдена: {db_path}")
            return
        
        # Создаем синхронную сессию
        db_url = f"sqlite:///{db_path}"
        sync_engine = create_engine(db_url, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(bind=sync_engine)
        
        with SessionLocal() as db:
            initialize_secondhands_sync(db)
            print("✅ Секондхенды успешно инициализированы!")
            
    except Exception as e:
        print(f"❌ Ошибка при инициализации: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_secondhands()

