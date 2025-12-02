# Backend/tests/test_initial_data.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import os
import pytest

from Backend.app.models.user import Base
from Backend.app.models.secondhand import Secondhand
from Backend.app.core.initial_data import initialize_secondhands, backup_secondhands

TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture
def db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_initialize_secondhands_creates_data_if_empty(db):
    """
    Если таблица пустая — initialize_secondhands должен создать тестовые записи.
    """
    count_before = db.query(Secondhand).count()
    assert count_before == 0

    initialize_secondhands(db)

    count_after = db.query(Secondhand).count()
    assert count_after > 0  # есть хотя бы несколько записей


def test_initialize_secondhands_is_idempotent(db):
    """
    Повторный вызов initialize_secondhands не должен дублировать данные.
    """
    initialize_secondhands(db)
    count_first = db.query(Secondhand).count()

    initialize_secondhands(db)
    count_second = db.query(Secondhand).count()

    assert count_first == count_second


def test_backup_secondhands_creates_json_file(db, tmp_path):
    """
    backup_secondhands должен создать JSON-файл с данными из БД.
    """
    # Подготовим данные
    initialize_secondhands(db)
    count_in_db = db.query(Secondhand).count()
    assert count_in_db > 0

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    backup_path = backup_secondhands(db, backup_dir=str(backup_dir))

    assert os.path.exists(backup_path)

    with open(backup_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == count_in_db
