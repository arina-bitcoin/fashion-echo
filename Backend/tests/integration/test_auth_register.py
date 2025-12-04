import pytest

# Чтобы не угадывать префиксы, берём их из openapi.json
async def _find_auth_paths(client):
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200, f"openapi unavailable: {resp.status_code} {resp.text}"
    doc = resp.json()
    paths = doc.get("paths", {})

    # Ищем любые пути, оканчивающиеся на нужные хвосты
    register = None
    login = None
    me = None

    for p in paths.keys():
        if p.endswith("/auth/register"):
            register = p
        if p.endswith("/auth/login"):
            login = p
        if p.endswith("/auth/me"):
            me = p

    # Подстраховка на редкие варианты (например, /api/v1/auth/*)
    assert register, f"Не найден путь для register в openapi.json. Доступные пути: {list(paths.keys())[:20]}"
    assert login, f"Не найден путь для login в openapi.json. Доступные пути: {list(paths.keys())[:20]}"
    assert me, f"Не найден путь для me в openapi.json. Доступные пути: {list(paths.keys())[:20]}"
    return register, login, me


@pytest.mark.asyncio
async def test_register_and_login_user(client, db_session):
    register_path, login_path, me_path = await _find_auth_paths(client)

    # 1) регистрация (твой код умеет принимать JSON body с email/password/full_name)
    resp = await client.post(
        register_path,
        json={"email": "newuser@example.com", "password": "password123", "full_name": "New User"},
    )
    assert resp.status_code == 200, f"register failed at {register_path}: {resp.status_code} {resp.text}"
    data = resp.json()
    assert data["email"] == "newuser@example.com"

    # 2) логин — через JSON (поддерживается в твоём обработчике)
    resp = await client.post(
        login_path,
        json={"email": "newuser@example.com", "password": "password123"},
    )
    assert resp.status_code == 200, f"login failed at {login_path}: {resp.status_code} {resp.text}"
    tokens = resp.json()
    assert "access_token" in tokens
    assert tokens.get("token_type") in {"bearer", "Bearer", None}  # некоторые реализации token_type опциональны

    # 3) /me с Bearer-токеном
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    me = await client.get(me_path, headers=headers)
    assert me.status_code == 200, f"/me failed at {me_path}: {me.status_code} {me.text}"
    me_data = me.json()
    assert me_data["email"] == "newuser@example.com"
