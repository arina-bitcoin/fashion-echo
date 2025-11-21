// auth-state.js - Исправленная версия с всеми методами
console.log('✅ auth-state.js loaded');

class AuthStateManager {
    constructor() {
        this.currentUser = null;
        this.allUsers = [];
        console.log('🔧 AuthStateManager created');
        this.init();
    }

    async init() {
        // Проверяем, есть ли токен и загружаем пользователя
        const token = localStorage.getItem('auth_token');
        if (token) {
            await this.loadCurrentUserFromAPI();
        }
        this.updateUI();
        this.setupEventListeners();
    }


    async loadCurrentUserFromAPI() {
        try {
            const userData = await apiService.getCurrentUser();
            this.currentUser = userData;
            console.log('📁 Current user loaded from API:', this.currentUser.name);
        } catch (error) {
            console.error('❌ Error loading current user from API:', error);
            this.currentUser = null;
            apiService.clearToken();
        }
    }


    // Сохранение всех пользователей
    saveAllUsersToStorage() {
        try {
            localStorage.setItem('fashioneco_all_users', JSON.stringify(this.allUsers));
            console.log('💾 All users saved:', this.allUsers.length);
            return true;
        } catch (error) {
            console.error('❌ Error saving users:', error);
            return false;
        }
    }

    // Сохранение текущего пользователя
    saveCurrentUserToStorage() {
        try {
            if (this.currentUser) {
                localStorage.setItem('fashioneco_current_user', JSON.stringify(this.currentUser));
                console.log('💾 Current user saved:', this.currentUser.name);
            } else {
                localStorage.removeItem('fashioneco_current_user');
                console.log('💾 Current user removed from storage');
            }
            return true;
        } catch (error) {
            console.error('❌ Error saving current user:', error);
            return false;
        }
    }

    // ЗАМЕНА: Регистрация через API
    async register(userData) {
        try {
            console.log('👤 Registering new user via API...');
            
            const response = await apiService.register({
                name: userData.name,
                email: userData.email,
                phone: userData.phone || '',
                password: userData.password
            });

            // Сохраняем токен
            if (response.token) {
                apiService.setToken(response.token);
            }

            // Устанавливаем текущего пользователя
            this.currentUser = response.user;
            this.updateUI();

            console.log('✅ New user registered via API:', this.currentUser.name);
            return this.currentUser;

        } catch (error) {
            console.error('❌ Registration failed:', error);
            throw error;
        }
    }

        async login(email, password) {
        try {
            console.log('🔐 Logging in via API...');
            
            const response = await apiService.login({
                email: email,
                password: password
            });

            // Сохраняем токен
            if (response.token) {
                apiService.setToken(response.token);
            }

            // Устанавливаем текущего пользователя
            this.currentUser = response.user;
            this.updateUI();

            console.log('✅ User logged in via API:', this.currentUser.name);
            return this.currentUser;

        } catch (error) {
            console.error('❌ Login failed:', error);
            throw error;
        }
    }


    async updateUserProfile(profileData) {
        if (!this.currentUser) {
            throw new Error('Пользователь не авторизован');
        }

        try {
            console.log('💾 Updating user profile via API...');
            
            const updatedUser = await apiService.updateProfile(profileData);
            
            // Обновляем текущего пользователя
            this.currentUser = updatedUser;
            this.updateUI();

            console.log('✅ Profile updated via API:', updatedUser.name);
            return updatedUser;

        } catch (error) {
            console.error('❌ Profile update failed:', error);
            throw error;
        }
    }

    async logout() {
        try {
            console.log('🚪 Logging out via API...');
            
            // Вызываем logout на сервере
            await apiService.logout();
            
        } catch (error) {
            console.error('❌ Logout API call failed:', error);
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

    // Обновление аватара
    async updateUserAvatar(avatarUrl) {
        return await this.updateUserProfile({
            avatar: avatarUrl
        });
    }

    async getUserById(userId) {
        try {
            const user = await apiService.getUserById(userId);
            return user;
        } catch (error) {
            console.error('❌ Error fetching user:', error);
            return null;
        }
    }

    // Получение пользователя по email
    getUserByEmail(email) {
        return this.allUsers.find(user => user.email === email);
    }

    async getAllUsers() {
        try {
            const users = await apiService.getAllUsers();
            return users;
        } catch (error) {
            console.error('❌ Error fetching users:', error);
            return [];
        }
    }

    // Генерация ID
    generateId() {
        return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    setupEventListeners() {
        // Обработчик для аватара
        const avatarBtn = document.getElementById('user-avatar-btn');
        if (avatarBtn) {
            avatarBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDropdown();
            });
        }

        // Обработчик для кнопок меню
        document.addEventListener('click', (e) => {
            const dropdown = document.querySelector('.user-dropdown-menu');
            
            // Клик по выходу
            if (e.target.id === 'logout-btn' || e.target.closest('#logout-btn')) {
                e.preventDefault();
                this.logout();
            }
            
            // Клик по профилю
            else if (e.target.id === 'profile-btn' || e.target.closest('#profile-btn')) {
                e.preventDefault();
                window.location.href = 'profile.html';
            }
            
            // Клик вне меню - скрываем
            else if (dropdown && !dropdown.contains(e.target) && avatarBtn && !avatarBtn.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });
    }

    toggleDropdown() {
        const dropdown = document.querySelector('.user-dropdown-menu');
        console.log('🎯 Toggling dropdown, current state:', dropdown.classList.contains('show'));
        
        if (dropdown) {
            dropdown.classList.toggle('show');
            console.log('🎯 New state:', dropdown.classList.contains('show') ? 'visible' : 'hidden');
        }
    }

    loadUserFromStorage() {
        try {
            const userData = localStorage.getItem('fashioneco_current_user');
            if (userData) {
                this.currentUser = JSON.parse(userData);
                console.log('📁 User loaded from storage:', this.currentUser);
            } else {
                console.log('📁 No user found in storage');
            }
        } catch (error) {
            console.error('❌ Error loading user from storage:', error);
            this.currentUser = null;
        }
    }

    saveUserToStorage(user) {
        try {
            localStorage.setItem('fashioneco_current_user', JSON.stringify(user));
            this.currentUser = user;
            this.updateUI();
            console.log('💾 User saved to storage:', user);
            return true;
        } catch (error) {
            console.error('❌ Error saving user to storage:', error);
            return false;
        }
    }

    
    // ДОБАВЛЯЕМ ОТСУТСТВУЮЩИЕ МЕТОДЫ:
    isLoggedIn() {
        return this.currentUser !== null;
    }

    getCurrentUser() {
        return this.currentUser;
    }

    updateUI() {
        const loginBtn = document.getElementById('login-btn');
        const avatarBtn = document.getElementById('user-avatar-btn');
        const avatarImg = document.getElementById('header-avatar');

        console.log('🎨 Updating UI...');
        console.log('  Login button:', loginBtn);
        console.log('  Avatar button:', avatarBtn);
        console.log('  User logged in:', this.isLoggedIn());

        if (this.isLoggedIn() && avatarBtn && avatarImg) {
            if (loginBtn) loginBtn.style.display = 'none';
            avatarBtn.style.display = 'block';

            if (this.currentUser.avatar) {
                avatarImg.src = this.currentUser.avatar;
            } else {
                this.createInitialsAvatar(avatarImg, this.currentUser.name);
            }
            console.log('✅ Showing avatar, hiding login button');
        } else {
            if (loginBtn) loginBtn.style.display = 'block';
            if (avatarBtn) avatarBtn.style.display = 'none';
            console.log('✅ Showing login button, hiding avatar');
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
}

// Создаем глобальный экземпляр
window.authState = new AuthStateManager();
