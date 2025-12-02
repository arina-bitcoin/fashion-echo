# Backend/tests/conftest.py

import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Backend.app.main import app
from Backend.app.core.database import Base, get_db
from Backend.app.core.security import get_password_hash, create_access_token
from Backend.app.models.user import User


# ---------- БАЗА ДАННЫХ ДЛЯ ТЕСТОВ ----------

@pytest.fixture(scope="session")
def db_engine():
    """
    Отдельная sqlite-база во временном файле для всех интеграционных тестов.
    """
    fd, path = tempfile.mkstemp()
    os.close(fd)

    engine = create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    os.remove(path)


@pytest.fixture()
def db_session(db_engine):
    """
    Отдельная сессия на каждый тест.
    """
    SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionTesting()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ---------- ПЕРЕОПРЕДЕЛЕНИЕ get_db ДЛЯ FASTAPI ----------

@pytest.fixture()
def client(db_session):
    """
    TestClient, у которого get_db подменён на тестовую сессию.
    """

    def _get_db_override():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_db_override

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ---------- ТЕСТОВЫЙ ПОЛЬЗОВАТЕЛЬ И АВТОРИЗАЦИЯ ----------

@pytest.fixture()
def test_user(db_session):
    """
    get-or-create пользователя с email=test@example.com,
    чтобы не ловить UNIQUE constraint.
    """
    user = db_session.query(User).filter_by(email="test@example.com").first()
    if user:
        return user

    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def auth_headers(test_user: User):
    """
    Делаем тот же токен, что и в /auth/login:
    create_access_token(data={"sub": str(user.id), "email": user.email})
    """
    token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email}
    )
    return {"Authorization": f"Bearer {token}"}
