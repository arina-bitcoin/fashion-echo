from Backend.app.models.user import User

def test_register_and_login_user(client, db_session):
    # 1. регистрация
    resp = client.post(
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
    login_resp = client.post(
        "/api/auth/login",
        params={  # у тебя login(email: str, password: str) → это query-параметры
            "email": "newuser@example.com",
            "password": "password123",
        },
    )
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    assert "access_token" in tokens

    # 3. проверяем, что юзер действительно в БД
    user_in_db = db_session.query(User).filter_by(email="newuser@example.com").first()
    assert user_in_db is not None
