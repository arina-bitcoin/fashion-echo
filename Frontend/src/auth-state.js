// auth-state.js - Исправленная версия с всеми методами
console.log('✅ auth-state.js loaded');

class AuthStateManager {
    constructor() {
        this.currentUser = null;
        console.log('🔧 AuthStateManager created');
        this.init();
    }

    init() {
        this.loadUserFromStorage();
        this.updateUI();
        this.setupEventListeners();
        console.log('🔧 Init completed, user:', this.currentUser ? 'logged in' : 'not logged in');
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

    logout() {
        console.log('🚪 Logging out...');
        this.currentUser = null;
        localStorage.removeItem('fashioneco_current_user');
        this.updateUI();
        
        // Скрываем меню
        const dropdown = document.querySelector('.user-dropdown-menu');
        if (dropdown) {
            dropdown.classList.remove('show');
        }
        
        alert('Вы успешно вышли из системы');
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