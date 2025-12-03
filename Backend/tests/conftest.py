import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from Backend.app.core.database import Base, get_db
from Backend.app.main import app
from Backend.app.models.user import User
from Backend.app.core.security import get_password_hash
from Backend.app.core.security import create_access_token



# --- ТЕСТОВАЯ БД: отдельный async-движок ---

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine_test,
    expire_on_commit=False,
    class_=AsyncSession,
)


# --- Перед КАЖДЫМ тестом: пересоздаём схему ---

@pytest_asyncio.fixture(autouse=True)
async def prepare_db():
    """
    Полностью пересоздаём структуру БД перед каждым тестом.
    Гарантия, что ни один пользователь `newuser@example.com`
    не "прилетит" из прошлых тестов/сидов.
    """
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # можно ничего не делать на teardown, но для чистоты:
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# --- Фикстура сессии для прямой работы с БД в тестах ---

@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()


# --- Переопределяем зависимость get_db в приложении ---

@pytest_asyncio.fixture
async def client():
    """
    AsyncClient, у которого get_db подменён на тестовую асинхронную сессию.
    """

    async def _get_db_override():
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.rollback()

    app.dependency_overrides[get_db] = _get_db_override

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# --- Тестовый пользователь для остальных интеграционных тестов ---

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """
    Создаём юзера с ИМЕЙЛОМ, ОТЛИЧНЫМ от newuser@example.com.
    Этот юзер нужен для других интеграционных тестов (users, ads и т.п.).
    """
    hashed = get_password_hash("password123")

    user = User(
        email="test@example.com",      # ВАЖНО: НЕ newuser@example.com
        name="Test User",
        hashed_password=hashed,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def auth_headers(test_user: User):
    """
    Возвращает заголовки Authorization для авторизованного пользователя test_user.
    Используется в интеграционных тестах (ads, files, users).
    """
    access_token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email}
    )
    return {"Authorization": f"Bearer {access_token}"}
