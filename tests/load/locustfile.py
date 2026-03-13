"""
Нагрузочное тестирование с помощью Locust
"""
import random
from locust import HttpUser, task, between


class FashionEcoUser(HttpUser):
    """Пользователь для нагрузочного тестирования"""
    
    wait_time = between(1, 3)  # Пауза между запросами 1-3 секунды
    
    def on_start(self):
        """Выполняется при старте каждого пользователя"""
        self.token = None
        self.user_id = None
        
        # Регистрируем пользователя
        user_data = {
            "email": f"loadtest_{random.randint(1000, 9999)}@example.com",
            "password": "testpassword123",
            "full_name": f"Load Test User {random.randint(1, 1000)}"
        }
        
        response = self.client.post("/api/auth/register", json=user_data)
        if response.status_code == 201:
            self.user_id = response.json()["id"]
            
            # Авторизуемся
            login_data = {
                "username": user_data["email"],
                "password": user_data["password"]
            }
            
            login_response = self.client.post("/api/auth/login", data=login_data)
            if login_response.status_code == 200:
                self.token = login_response.json()["access_token"]
    
    @property
    def headers(self):
        """Заголовки с токеном авторизации"""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    @task(10)
    def view_homepage(self):
        """Просмотр главной страницы"""
        self.client.get("/")
    
    @task(8)
    def health_check(self):
        """Проверка health endpoint"""
        self.client.get("/health")
    
    @task(15)
    def search_ads(self):
        """Поиск объявлений"""
        search_terms = ["одежда", "куртка", "джинсы", "платье", "обувь", "сумка"]
        term = random.choice(search_terms)
        self.client.get(f"/api/ads/search?q={term}")
    
    @task(12)
    def view_ads_list(self):
        """Просмотр списка объявлений"""
        page = random.randint(1, 5)
        self.client.get(f"/api/ads/?page={page}&limit=20")
    
    @task(5)
    def view_ad_detail(self):
        """Просмотр детальной страницы объявления"""
        # Сначала получаем список объявлений
        response = self.client.get("/api/ads/?limit=10")
        if response.status_code == 200:
            ads = response.json().get("items", [])
            if ads:
                ad_id = random.choice(ads)["id"]
                self.client.get(f"/api/ads/{ad_id}")
    
    @task(3)
    def create_ad(self):
        """Создание объявления (только авторизованные пользователи)"""
        if not self.token:
            return
            
        ad_data = {
            "title": f"Тестовое объявление {random.randint(1, 1000)}",
            "description": "Описание тестового объявления для нагрузочного тестирования",
            "price": random.randint(100, 5000),
            "category": random.choice(["clothing", "shoes", "accessories"]),
            "condition": random.choice(["new", "good", "fair", "poor"])
        }
        
        self.client.post("/api/ads/", json=ad_data, headers=self.headers)
    
    @task(2)
    def view_profile(self):
        """Просмотр профиля (только авторизованные пользователи)"""
        if not self.token:
            return
            
        self.client.get("/api/users/me", headers=self.headers)
    
    @task(2)
    def view_my_ads(self):
        """Просмотр своих объявлений (только авторизованные пользователи)"""
        if not self.token:
            return
            
        self.client.get("/api/ads/my", headers=self.headers)
    
    @task(1)
    def update_profile(self):
        """Обновление профиля (только авторизованные пользователи)"""
        if not self.token:
            return
            
        profile_data = {
            "full_name": f"Updated User {random.randint(1, 1000)}",
            "phone": f"+7900{random.randint(1000000, 9999999)}"
        }
        
        self.client.put("/api/users/me", json=profile_data, headers=self.headers)


class AnonymousUser(HttpUser):
    """Анонимный пользователь (без регистрации)"""
    
    wait_time = between(2, 5)
    weight = 3  # Больше анонимных пользователей
    
    @task(20)
    def browse_ads(self):
        """Просмотр объявлений"""
        page = random.randint(1, 10)
        self.client.get(f"/api/ads/?page={page}&limit=20")
    
    @task(15)
    def search_ads(self):
        """Поиск объявлений"""
        search_terms = ["куртка", "джинсы", "платье", "обувь", "сумка", "рубашка"]
        term = random.choice(search_terms)
        self.client.get(f"/api/ads/search?q={term}")
    
    @task(10)
    def view_ad_detail(self):
        """Просмотр детальной страницы объявления"""
        response = self.client.get("/api/ads/?limit=10")
        if response.status_code == 200:
            ads = response.json().get("items", [])
            if ads:
                ad_id = random.choice(ads)["id"]
                self.client.get(f"/api/ads/{ad_id}")
    
    @task(5)
    def view_categories(self):
        """Просмотр категорий"""
        self.client.get("/api/categories/")
    
    @task(3)
    def health_check(self):
        """Проверка health endpoint"""
        self.client.get("/health")


class AdminUser(HttpUser):
    """Администратор для тестирования админских функций"""
    
    wait_time = between(5, 10)
    weight = 1  # Мало админов
    
    def on_start(self):
        """Авторизация как админ"""
        # В реальном приложении здесь была бы авторизация админа
        pass
    
    @task(5)
    def view_all_users(self):
        """Просмотр всех пользователей"""
        self.client.get("/api/admin/users/")
    
    @task(3)
    def view_statistics(self):
        """Просмотр статистики"""
        self.client.get("/api/admin/stats/")
    
    @task(2)
    def moderate_ads(self):
        """Модерация объявлений"""
        self.client.get("/api/admin/ads/pending/")


# Конфигурация для запуска
if __name__ == "__main__":
    import os
    from locust import run_single_user
    
    # Запуск одного пользователя для отладки
    run_single_user(FashionEcoUser)