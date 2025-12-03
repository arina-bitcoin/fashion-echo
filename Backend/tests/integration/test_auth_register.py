import pytest
from sqlalchemy import select

from Backend.app.models.user import User


@pytest.mark.asyncio
async def test_register_and_login_user(client, db_session):
    # 1. регистрация
    resp = await client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "newuser@example.com"

    # 2. логин
    login_resp = await client.post(
        "/api/auth/login",
        params={
            "email": "newuser@example.com",
            "password": "password123",
        },
    )
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    assert "access_token" in tokens

    # 3. проверяем, что юзер действительно в БД
    result = await db_session.execute(
        select(User).where(User.email == "newuser@example.com")
    )
    user_in_db = result.scalar_one_or_none()
    assert user_in_db is not None
