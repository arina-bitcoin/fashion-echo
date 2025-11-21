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
        } catch (error) {
            console.error('❌ Error loading current user from API:', error);
            
            // Если ошибка (например, невалидный токен) - очищаем состояние
            this.currentUser = null;
            apiService.clearToken();
            
            console.log('🔄 Cleared invalid token and user data');
        }
    }

    // РЕГИСТРАЦИЯ
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

            // Сохраняем токен если он есть в ответе
            if (response.token) {
                apiService.setToken(response.token);
                
                // Загружаем данные пользователя с бекенда
                await this.loadCurrentUserFromAPI();
            } else {
                // Если токена нет, создаем пользователя из response
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
            console.log('✅ New user registered via API:', this.currentUser?.name);
            return this.currentUser;

        } catch (error) {
            console.error('❌ Registration failed:', error);
            throw error;
        }
    }

    // ЛОГИН - ТОЛЬКО ЧЕРЕЗ API
    async login(email, password) {
        try {
            console.log('🔐 Logging in via API...');
            
            const response = await apiService.login({
                email: email,
                password: password
            });

            console.log('📨 Login response:', response);

            // Сохраняем токен
            if (response.token) {
                apiService.setToken(response.token);
                
                // Загружаем данные пользователя с бекенда
                await this.loadCurrentUserFromAPI();
            } else {
                throw new Error('No token in login response');
            }

            this.updateUI();
            console.log('✅ User logged in via API:', this.currentUser?.name);
            return this.currentUser;

        } catch (error) {
            console.error('❌ Login failed:', error);
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
                if (this.currentUser.avatar) {
                    avatarImg.src = this.currentUser.avatar;
                } else {
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