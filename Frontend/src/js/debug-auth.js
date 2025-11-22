// debug-auth.js - ТЕСТЫ ДЛЯ ДИАГНОСТИКИ АВТОРИЗАЦИИ
console.log('🔧 DEBUG AUTH - ЗАПУСК ТЕСТОВ');

class AuthDebugger {
    constructor() {
        this.runAllTests();
    }

    async runAllTests() {
        console.log('\n🎯 ===== ЗАПУСК ДИАГНОСТИКИ АВТОРИЗАЦИИ =====\n');
        
        await this.testLocalStorage();
        await this.testApiService();
        await this.testAuthState();
        await this.testUIState();
        await this.testTokenValidity();
        
        console.log('\n🎯 ===== ДИАГНОСТИКА ЗАВЕРШЕНА =====\n');
        this.showSummary();
    }

    // ТЕСТ 1: Проверка localStorage
    async testLocalStorage() {
        console.log('🔍 ТЕСТ 1: Проверка localStorage');
        
        const token = localStorage.getItem('auth_token');
        const userData = localStorage.getItem('fashioneco_current_user');
        
        console.log('📦 auth_token:', token ? '✅ Присутствует' : '❌ Отсутствует');
        console.log('📦 fashioneco_current_user:', userData ? '✅ Присутствует' : '❌ Отсутствует');
        
        if (token) {
            console.log('🔑 Токен (первые 20 символов):', token.substring(0, 20) + '...');
        }
        
        if (userData) {
            try {
                const user = JSON.parse(userData);
                console.log('👤 Данные пользователя:', user);
            } catch (e) {
                console.log('❌ Ошибка парсинга userData:', e);
            }
        }
        
        console.log('---\n');
    }

    // ТЕСТ 2: Проверка ApiService
    async testApiService() {
        console.log('🔍 ТЕСТ 2: Проверка ApiService');
        
        if (!window.apiService) {
            console.log('❌ ApiService не загружен в window');
            return;
        }
        
        console.log('🔧 ApiService:', window.apiService ? '✅ Загружен' : '❌ Отсутствует');
        console.log('🔑 Token в ApiService:', window.apiService.token ? '✅ Есть' : '❌ Нет');
        console.log('🌐 BASE_URL:', window.apiService.BASE_URL);
        
        // Проверяем методы
        const methods = ['request', 'login', 'register', 'getCurrentUser'];
        methods.forEach(method => {
            console.log(`🔧 ${method}:`, typeof window.apiService[method] === 'function' ? '✅ Доступен' : '❌ Отсутствует');
        });
        
        console.log('---\n');
    }

    // ТЕСТ 3: Проверка AuthState
    async testAuthState() {
        console.log('🔍 ТЕСТ 3: Проверка AuthState');
        
        if (!window.authState) {
            console.log('❌ AuthState не загружен в window');
            return;
        }
        
        console.log('🔧 AuthState:', window.authState ? '✅ Загружен' : '❌ Отсутствует');
        console.log('👤 Текущий пользователь:', window.authState.currentUser);
        console.log('🔐 isLoggedIn():', window.authState.isLoggedIn ? window.authState.isLoggedIn() : '❌ Метод недоступен');
        
        if (window.authState.currentUser) {
            console.log('📋 Данные пользователя в AuthState:', window.authState.currentUser);
        }
        
        console.log('---\n');
    }

    // ТЕСТ 4: Проверка UI состояния
    async testUIState() {
        console.log('🔍 ТЕСТ 4: Проверка UI состояния');
        
        const loginBtn = document.getElementById('login-btn');
        const avatarBtn = document.getElementById('user-avatar-btn');
        const dropdown = document.querySelector('.user-dropdown-menu');
        
        console.log('🎨 Кнопка входа:', loginBtn ? `✅ Найдена (display: ${getComputedStyle(loginBtn).display})` : '❌ Не найдена');
        console.log('🎨 Аватар пользователя:', avatarBtn ? `✅ Найден (display: ${getComputedStyle(avatarBtn).display})` : '❌ Не найден');
        console.log('🎨 Выпадающее меню:', dropdown ? '✅ Найдено' : '❌ Не найдено');
        
        if (avatarBtn) {
            const avatarImg = document.getElementById('header-avatar');
            console.log('🖼️ Изображение аватара:', avatarImg ? `✅ Найдено (src: ${avatarImg.src})` : '❌ Не найдено');
        }
        
        console.log('---\n');
    }

    // ТЕСТ 5: Проверка валидности токена
    async testTokenValidity() {
        console.log('🔍 ТЕСТ 5: Проверка валидности токена');
        
        const token = localStorage.getItem('auth_token');
        
        if (!token) {
            console.log('❌ Токен отсутствует - пользователь не авторизован');
            return;
        }
        
        console.log('🔑 Токен найден, проверяем валидность...');
        
        try {
            // Пытаемся получить данные пользователя
            if (window.apiService) {
                console.log('🔄 Запрос к /auth/me...');
                const userData = await window.apiService.getCurrentUser();
                console.log('✅ Токен валиден! Данные пользователя:', userData);
            } else {
                console.log('⚠️ ApiService недоступен для проверки токена');
            }
        } catch (error) {
            console.log('❌ Токен невалиден:', error.message);
            console.log('💡 Рекомендация: очистить токен и перелогиниться');
            
            // Автоматически очищаем невалидный токен
            localStorage.removeItem('auth_token');
            console.log('🗑️ Невалидный токен удален из localStorage');
        }
        
        console.log('---\n');
    }

    showSummary() {
        console.log('📊 ИТОГОВАЯ СВОДКА:');
        
        const token = localStorage.getItem('auth_token');
        const userData = localStorage.getItem('fashioneco_current_user');
        const isAuthStateReady = window.authState && window.authState.isLoggedIn && window.authState.isLoggedIn();
        
        console.log('🔐 Пользователь авторизован:', token && isAuthStateReady ? '✅ ДА' : '❌ НЕТ');
        
        if (token && !isAuthStateReady) {
            console.log('🚨 ПРОБЛЕМА: Токен есть, но AuthState не считает пользователя авторизованным');
            console.log('💡 Возможные причины:');
            console.log('   1. AuthState не успел инициализироваться');
            console.log('   2. Токен невалидный');
            console.log('   3. Ошибка в методе loadCurrentUserFromAPI()');
        }
        
        if (!token && userData) {
            console.log('🚨 ПРОБЛЕМА: Нет токена, но есть данные пользователя');
            console.log('💡 Возможные причины:');
            console.log('   1. Пользователь вышел из системы');
            console.log('   2. Токен был удален/истек');
        }
        
        console.log('\n💡 КОМАНДЫ ДЛЯ РУЧНОЙ ПРОВЕРКИ:');
        console.log('   localStorage.getItem("auth_token")');
        console.log('   window.authState.getCurrentUser()');
        console.log('   window.apiService.getCurrentUser()');
    }
}

// Запуск диагностики при загрузке
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        window.authDebugger = new AuthDebugger();
    }, 1000);
});

// Экспорт для ручного запуска
window.runAuthTests = function() {
    return new AuthDebugger();
};