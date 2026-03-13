"""
Интеграционные тесты API
"""
import asyncio
import pytest
import httpx
from typing import AsyncGenerator


@pytest.fixture(scope="session")
def event_loop():
    """Создаем event loop для всей сессии тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """HTTP клиент для тестирования API"""
    base_url = "http://backend-test:8000"
    
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        # Ждем, пока API станет доступным
        for _ in range(30):
            try:
                response = await client.get("/health")
                if response.status_code == 200:
                    break
            except httpx.ConnectError:
                await asyncio.sleep(1)
        else:
            pytest.fail("API не стал доступен в течение 30 секунд")
        
        yield client


@pytest.mark.asyncio
async def test_health_check(client: httpx.AsyncClient):
    """Тест health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_api_docs_available(client: httpx.AsyncClient):
    """Тест доступности документации API"""
    response = await client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()


@pytest.mark.asyncio
async def test_user_registration_flow(client: httpx.AsyncClient):
    """Тест полного флоу регистрации пользователя"""
    # Регистрация
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    
    user = response.json()
    assert user["email"] == user_data["email"]
    assert user["full_name"] == user_data["full_name"]
    assert "id" in user


@pytest.mark.asyncio
async def test_user_login_flow(client: httpx.AsyncClient):
    """Тест флоу авторизации пользователя"""
    # Сначала регистрируем пользователя
    user_data = {
        "email": "login_test@example.com",
        "password": "testpassword123",
        "full_name": "Login Test User"
    }
    
    await client.post("/api/auth/register", json=user_data)
    
    # Авторизация
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    
    response = await client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    
    tokens = response.json()
    assert "access_token" in tokens
    assert "token_type" in tokens
    assert tokens["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client: httpx.AsyncClient):
    """Тест защищенного endpoint без токена"""
    response = await client.get("/api/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_token(client: httpx.AsyncClient):
    """Тест защищенного endpoint с токеном"""
    # Регистрация и авторизация
    user_data = {
        "email": "protected_test@example.com",
        "password": "testpassword123",
        "full_name": "Protected Test User"
    }
    
    await client.post("/api/auth/register", json=user_data)
    
    login_response = await client.post("/api/auth/login", data={
        "username": user_data["email"],
        "password": user_data["password"]
    })
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Запрос к защищенному endpoint
    response = await client.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    
    user = response.json()
    assert user["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_create_and_get_ad(client: httpx.AsyncClient):
    """Тест создания и получения объявления"""
    # Регистрация и авторизация
    user_data = {
        "email": "ad_test@example.com",
        "password": "testpassword123",
        "full_name": "Ad Test User"
    }
    
    await client.post("/api/auth/register", json=user_data)
    
    login_response = await client.post("/api/auth/login", data={
        "username": user_data["email"],
        "password": user_data["password"]
    })
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Создание объявления
    ad_data = {
        "title": "Тестовое объявление",
        "description": "Описание тестового объявления",
        "price": 1000,
        "category": "clothing",
        "condition": "good"
    }
    
    response = await client.post("/api/ads/", json=ad_data, headers=headers)
    assert response.status_code == 201
    
    ad = response.json()
    assert ad["title"] == ad_data["title"]
    assert ad["price"] == ad_data["price"]
    ad_id = ad["id"]
    
    # Получение объявления
    response = await client.get(f"/api/ads/{ad_id}")
    assert response.status_code == 200
    
    retrieved_ad = response.json()
    assert retrieved_ad["id"] == ad_id
    assert retrieved_ad["title"] == ad_data["title"]


@pytest.mark.asyncio
async def test_search_ads(client: httpx.AsyncClient):
    """Тест поиска объявлений"""
    response = await client.get("/api/ads/search?q=тест")
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_database_connection(client: httpx.AsyncClient):
    """Тест подключения к базе данных через API"""
    response = await client.get("/api/health/db")
    assert response.status_code == 200
    
    data = response.json()
    assert data["database"] == "connected"

