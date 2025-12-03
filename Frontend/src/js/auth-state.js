// auth-state.js - ПРАВИЛЬНАЯ АРХИТЕКТУРА
console.log('✅ auth-state.js loaded');

class AuthStateManager {
    constructor() {
        this.currentUser = null;
        console.log('🔧 AuthStateManager created');
        this.init();
    }

    async init() {
        console.log('🔄 Initializing AuthStateManager...');
        
        // 1. Проверяем есть ли токен
        const token = localStorage.getItem('auth_token');
        
        if (token) {
            // 2. Если есть токен - загружаем пользователя с бекенда
            await this.loadCurrentUserFromAPI();
        } else {
            // 3. Если нет токена - очищаем состояние
            this.currentUser = null;
        }
        
        // 4. Обновляем UI
        this.updateUI();
        
        // 5. Настраиваем обработчики событий
        this.setupEventListeners();
        
        console.log('✅ AuthStateManager initialized');
        console.log('👤 Current user:', this.currentUser);
        console.log('🔐 Is logged in:', this.isLoggedIn());
    }

    async loadCurrentUserFromAPI() {
        try {
            console.log('📡 Loading current user from API...');
            const userData = await apiService.getCurrentUser();
            this.currentUser = userData;
            console.log('✅ Current user loaded from API:', this.currentUser);
            console.log('🖼️ Avatar data:', {
                avatar: this.currentUser.avatar,
                avatar_url: this.currentUser.avatar_url
            });
            
            // ВАЖНО: Обновляем UI после загрузки данных пользователя
            this.updateUI();
        } catch (error) {
            console.error('❌ Error loading current user from API:', error);
            
            // Если ошибка (например, невалидный токен) - очищаем состояние
            this.currentUser = null;
            apiService.clearToken();
            
            console.log('🔄 Cleared invalid token and user data');
            
            // Обновляем UI после очистки
            this.updateUI();
        }
    }

    // РЕГИСТРАЦИЯ
    async login(email, password) {
    try {
        console.log('🔐 Logging in via API...');
        
        const response = await apiService.login({
            email: email,
            password: password
        });

        console.log('📨 Login response:', response);

        // Проверяем наличие access_token в ответе
        if (response.access_token) {
            apiService.setToken(response.access_token);
            
            // ОПТИМИЗАЦИЯ: Загружаем пользователя асинхронно, не блокируя переход
            // Это ускоряет процесс входа - пользователь увидит главную страницу быстрее
            this.loadCurrentUserFromAPI().catch(error => {
                console.warn('⚠️ Failed to load user data after login (non-critical):', error);
            });
        } else {
            // ДОБАВЛЯЕМ ДЕТАЛЬНУЮ ОТЛАДКУ
            console.log('🔍 Token debug - response keys:', Object.keys(response));
            console.log('🔍 Available tokens:', {
                access_token: response.access_token,
                refresh_token: response.refresh_token,
                token_type: response.token_type
            });
            throw new Error('No access_token in login response');
        }

        this.updateUI();
        console.log('✅ User logged in via API:', this.currentUser?.name);
        return this.currentUser;

    } catch (error) {
        console.error('❌ Login failed:', error);
        throw error;
    }
}

// ТАКЖЕ ИСПРАВЛЯЕМ МЕТОД РЕГИСТРАЦИИ ДЛЯ АВТО-ЛОГИНА
async register(userData) {
    try {
        console.log('👤 Registering new user via API...');
        
        const response = await apiService.register({
            name: userData.name,
            email: userData.email,
            phone: userData.phone || '',
            password: userData.password
        });

        console.log('📨 Registration response:', response);

        // АВТОМАТИЧЕСКИ ВХОДИМ ПОСЛЕ УСПЕШНОЙ РЕГИСТРАЦИИ
        console.log('🔐 Auto-login after registration...');
        try {
            const loginResponse = await apiService.login({
                email: userData.email,
                password: userData.password
            });
            
            // ИСПРАВЛЕНИЕ: Проверяем access_token
            if (loginResponse.access_token) {
                apiService.setToken(loginResponse.access_token);
                console.log('✅ Auto-login successful, token saved');
                
                // Загружаем данные пользователя
                await this.loadCurrentUserFromAPI();
            } else {
                console.log('❌ No access_token in auto-login response');
                throw new Error('Auto-login failed: no token received');
            }
        } catch (loginError) {
            console.log('⚠️ Auto-login failed:', loginError.message);
            // Если авто-логин не удался, создаем пользователя из response регистрации
            this.currentUser = {
                id: response.id,
                name: response.name,
                email: response.email,
                phone: userData.phone || '',
                avatar: null,
                isActive: response.is_active !== false,
                isVerified: response.is_verified || false,
                registeredAt: response.created_at || new Date().toISOString(),
                lastLogin: new Date().toISOString()
            };
        }

        this.updateUI();
        console.log('✅ New user registered:', this.currentUser?.name);
        return this.currentUser;

    } catch (error) {
        console.error('❌ Registration failed:', error);
        throw error;
    }
}
    // ВЫХОД
    async logout() {
        try {
            console.log('🚪 Logging out...');
            
            // Пытаемся вызвать logout на сервере
            try {
                await apiService.logout();
            } catch (error) {
                console.log('⚠️ Logout API call failed (ignoring):', error.message);
            }
            
        } finally {
            // Всегда очищаем локальные данные
            this.currentUser = null;
            apiService.clearToken();
            this.updateUI();
            
            // Скрываем меню
            const dropdown = document.querySelector('.user-dropdown-menu');
            if (dropdown) {
                dropdown.classList.remove('show');
            }
            
            console.log('✅ User logged out');
        }
    }

    // UI методы
    updateUI() {
        console.log('🎨 Updating UI...');
        
        const loginBtn = document.getElementById('login-btn');
        const avatarBtn = document.getElementById('user-avatar-btn');
        const avatarImg = document.getElementById('header-avatar');

        console.log('🔐 User logged in:', this.isLoggedIn());
        console.log('👤 Current user:', this.currentUser);

        if (this.isLoggedIn() && this.currentUser) {
            console.log('🟢 Showing authenticated UI');
            
            if (loginBtn) loginBtn.style.display = 'none';
            if (avatarBtn) avatarBtn.style.display = 'block';

            if (avatarImg) {
                // ИСПРАВЛЕНИЕ: Проверяем avatar_url в первую очередь (сервер возвращает его)
                // Если нет avatar_url, проверяем avatar и формируем URL
                let avatarUrl = null;
                
                if (this.currentUser.avatar_url) {
                    // Используем готовый URL с сервера
                    avatarUrl = this.currentUser.avatar_url;
                } else if (this.currentUser.avatar) {
                    // Если есть только путь к файлу, формируем полный URL
                    const avatarPath = this.currentUser.avatar;
                    const cleanPath = avatarPath.startsWith('/') ? avatarPath.slice(1) : avatarPath;
                    avatarUrl = `http://localhost:8000/static/${cleanPath}`;
                }
                
                if (avatarUrl) {
                    // Устанавливаем аватар с обработкой ошибок
                    avatarImg.onerror = () => {
                        console.warn('⚠️ Failed to load avatar image, using initials');
                        this.createInitialsAvatar(avatarImg, this.currentUser.name);
                    };
                    avatarImg.onload = () => {
                        console.log('✅ Avatar image loaded successfully');
                    };
                    avatarImg.src = avatarUrl;
                    avatarImg.style.display = 'block';
                } else {
                    // Если аватара нет, создаем инициалы
                    // Очищаем src перед созданием инициалов
                    avatarImg.onerror = null;
                    avatarImg.onload = null;
                    this.createInitialsAvatar(avatarImg, this.currentUser.name);
                }
            }
            
        } else {
            console.log('🔴 Showing unauthenticated UI');
            
            if (loginBtn) loginBtn.style.display = 'block';
            if (avatarBtn) avatarBtn.style.display = 'none';
        }
    }

    createInitialsAvatar(imgElement, userName) {
        const names = userName.split(' ');
        let initials = names.length >= 2 
            ? names[0].charAt(0) + names[1].charAt(0)
            : names[0].charAt(0);

        const canvas = document.createElement('canvas');
        canvas.width = 40;
        canvas.height = 40;
        const ctx = canvas.getContext('2d');

        ctx.fillStyle = '#4B0505';
        ctx.fillRect(0, 0, 40, 40);

        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(initials.toUpperCase(), 20, 20);

        imgElement.src = canvas.toDataURL();
    }

    // Event listeners
    setupEventListeners() {
        const avatarBtn = document.getElementById('user-avatar-btn');
        if (avatarBtn) {
            avatarBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDropdown();
            });
        }

        document.addEventListener('click', (e) => {
            const dropdown = document.querySelector('.user-dropdown-menu');
            
            if (e.target.id === 'logout-btn' || e.target.closest('#logout-btn')) {
                e.preventDefault();
                this.logout();
            } else if (e.target.id === 'profile-btn' || e.target.closest('#profile-btn')) {
                e.preventDefault();
                window.location.href = 'profile.html';
            } else if (dropdown && !dropdown.contains(e.target) && avatarBtn && !avatarBtn.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });
    }

    toggleDropdown() {
        const dropdown = document.querySelector('.user-dropdown-menu');
        if (dropdown) {
            dropdown.classList.toggle('show');
        }
    }

    // Basic methods
    isLoggedIn() {
        return this.currentUser !== null;
    }

    getCurrentUser() {
        return this.currentUser;
    }
}

// Создаем глобальный экземпляр
window.authState = new AuthStateManager();
console.log('✅ AuthStateManager ready');