# Backend/tests/conftest.py
import io
from uuid import uuid4
from datetime import datetime, timedelta, timezone

import jwt  # PyJWT
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.app.main import app
from Backend.app.config import settings
from Backend.app.core.database import async_session_maker
from Backend.app.models.user import User
from Backend.app.models.ad import Ad


# ---------- ПАТЧИ БЕЗОПАСНОСТИ ДЛЯ ТЕСТОВ (убираем argon2) ----------
@pytest.fixture(autouse=True)
def _patch_password_hash_and_verify(monkeypatch):
    """
    В проде используется argon2, но в тестовой среде может не быть backend'а.
    Подменяем функции, чтобы регистрация/логин не падали.
    """
    from Backend.app.core import security

    def fake_hash(_password: str) -> str:
        return "hashed"  # фиксированная заглушка

    def fake_verify(plain: str, hashed: str) -> bool:
        # допускаем любой пароль, если сохранённая строка — наша заглушка
        return hashed == "hashed"

    monkeypatch.setattr(security, "get_password_hash", fake_hash, raising=True)
    monkeypatch.setattr(security, "verify_password", fake_verify, raising=True)


# ---------- ТЕСТОВЫЙ КЛИЕНТ ----------
@pytest_asyncio.fixture
async def client():
    """
    httpx >= 0.28: используем ASGITransport вместо app=...
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------- СЕССИЯ БД ----------
@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


# ---------- ТЕСТОВЫЕ ДАННЫЕ ----------
@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """
    Создаём юзера с уникальным email, чтобы не ловить UNIQUE при многократном использовании.
    Пароль не используется напрямую (логин/регистрация идут через наши заглушки).
    """
    u = User(
        email=f"test+{uuid4().hex}@example.com",
        hashed_password="hashed",   # соответствует fake_hash()
        name="Test User",
        phone=None,
        is_active=True,
        is_verified=False,
    )
    db_session.add(u)
    await db_session.commit()
    await db_session.refresh(u)
    return u


@pytest_asyncio.fixture
async def test_ad(db_session: AsyncSession, test_user: User) -> Ad:
    ad = Ad(
        title="Jacket",
        description="Nice jacket",
        category="clothes",
        price=1000,
        user_id=test_user.id,
        type="sell",
        size="M",
        condition="used",
        city="TestCity",
    )
    db_session.add(ad)
    await db_session.commit()
    await db_session.refresh(ad)
    return ad


# ---------- JWT (в обход продового create_access_token) ----------
def _make_access_token_for(user: User, minutes: int | None = None) -> str:
    exp_delta = timedelta(
        minutes=minutes if minutes is not None else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "type": "access",
        "exp": datetime.now(timezone.utc) + exp_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@pytest_asyncio.fixture
async def auth_headers(test_user: User):
    token = _make_access_token_for(test_user)
    return {"Authorization": f"Bearer {token}"}


# ---------- Мелкие утилиты для загрузки ----------
@pytest.fixture
def small_png_bytes() -> bytes:
    # 1x1 PNG
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00"
        b"\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc`\x00\x00\x00\x02\x00\x01"
        b"\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
    )


@pytest.fixture
def small_png_file(small_png_bytes: bytes):
    return ("test.png", io.BytesIO(small_png_bytes), "image/png")


@pytest.fixture(autouse=True)
def _patch_password_hash_and_verify(monkeypatch):
    # Патчим как исходный модуль безопасности, так и ссылки,
    # импортированные непосредственно внутрь эндпоинтов auth.
    from Backend.app.core import security
    from Backend.app.api.endpoints import auth as auth_ep

    def fake_hash(_password: str) -> str:
        # фиктивный хэш, чтобы не тянуть argon2/bcrypt и не падать в тестах
        return "hashed"

    def fake_verify(plain: str, hashed: str) -> bool:
        # считаем корректным любой пароль, если в БД хранится "hashed"
        return hashed == "hashed"

    # патчим исходный модуль безопасности
    monkeypatch.setattr(security, "get_password_hash", fake_hash, raising=True)
    monkeypatch.setattr(security, "verify_password", fake_verify, raising=True)

    # ОБЯЗАТЕЛЬНО патчим ссылки, импортированные внутрь эндпоинтов
    monkeypatch.setattr(auth_ep, "get_password_hash", fake_hash, raising=True)
    monkeypatch.setattr(auth_ep, "verify_password", fake_verify, raising=True)