# Backend/tests/test_user_settings.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import asyncio
import pytest

from Backend.app.models.user import Base, User
from Backend.app.schemas.user import UserUpdate, UserSettings
from Backend.app.api.endpoints.users import update_current_user

# Отдельный синхронный движок для тестов (in-memory SQLite)
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


@pytest.fixture(autouse=True)
def setup_db():
    """
    Для каждого теста создаём и очищаем таблицы
    на отдельном тестовом движке.
    """
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


def create_user(db, email="test@example.com"):
    user = User(
        email=email,
        hashed_password="fake_hash",
        full_name="Old Name",
        phone="+70000000000",
        is_active=True,
        is_verified=False,
        settings={
            "notifications": True,
            "theme": "light",
            "language": "ru",
            "email_notifications": True,
        },
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_partial_update_user_settings(db):
    """
    Проверяем, что при частичном обновлении настроек они мержатся,
    а не затирают старые ключи.
    """
    user = create_user(db)

    update_model = UserUpdate(
        settings=UserSettings(theme="dark")  # меняем только тему
    )

    updated_user = asyncio.run(
        update_current_user(
            user_data=update_model,
            db=db,
            current_user=user,
        )
    )

    assert updated_user.settings["theme"] == "dark"
    # Остальные настройки должны остаться
    assert updated_user.settings["notifications"] is True
    assert updated_user.settings["language"] == "ru"
    assert updated_user.settings["email_notifications"] is True


def test_update_user_profile_fields(db):
    """
    Проверяем, что обычные поля (full_name, phone) обновляются корректно.
    """
    user = create_user(db)

    update_model = UserUpdate(
        full_name="New Name",
        phone="+71111111111",
    )

    updated_user = asyncio.run(
        update_current_user(
            user_data=update_model,
            db=db,
            current_user=user,
        )
    )

    assert updated_user.full_name == "New Name"
    assert updated_user.phone == "+71111111111"
    # Настройки при этом не должны пропасть
    assert updated_user.settings["theme"] == "light"
    assert updated_user.settings["notifications"] is True


def test_update_without_settings_keeps_existing_settings(db):
    """
    Если в запросе нет поля settings, существующие настройки
    должны остаться без изменений.
    """
    user = create_user(db)

    update_model = UserUpdate(full_name="Another Name")

    updated_user = asyncio.run(
        update_current_user(
            user_data=update_model,
            db=db,
            current_user=user,
        )
    )

    assert updated_user.full_name == "Another Name"
    # Настройки остались как были
    assert updated_user.settings["theme"] == "light"
    assert updated_user.settings["notifications"] is True
    assert updated_user.settings["language"] == "ru"
    assert updated_user.settings["email_notifications"] is True
