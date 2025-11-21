// profile.js - Полная версия с глобальным сохранением
class UserProfile {
    constructor() {
        this.originalValues = {};
        this.isEditing = false;
        this.hasCustomAvatar = false;
        
        this.elements = {
            profileForm: document.getElementById('profile-form'),
            editButtons: document.querySelectorAll('.edit-btn'),
            cancelBtn: document.getElementById('cancel-btn'),
            saveBtn: document.getElementById('save-btn'),
            backBtn: document.getElementById('back-btn'),
            userAvatar: document.getElementById('user-avatar'),
            avatarImage: document.getElementById('avatar-image'),
            avatarInitials: document.getElementById('avatar-initials'),
            avatarInput: document.getElementById('avatar-input'),
            changeAvatarBtn: document.getElementById('change-avatar-btn'),
            removeAvatarBtn: document.getElementById('remove-avatar-btn'),
            userNameInput: document.getElementById('user-name'),
            userEmailInput: document.getElementById('user-email'),
            userPhoneInput: document.getElementById('user-phone')
        };

        console.log('🔧 UserProfile initialized');
        this.initializeElements();
        this.attachEventListeners();
        this.loadUserData();
    }

    initializeElements() {
        // Проверяем, что все элементы найдены
        for (const key in this.elements) {
            if (!this.elements[key]) {
                console.error(`Element not found: ${key}`);
            }
        }
        
        console.log('✅ All profile elements initialized');
    }

    loadUserData() {
        // Загружаем данные из authState если пользователь авторизован
        if (this.isAuthStateAvailable()) {
            const currentUser = this.getCurrentUser();
            if (currentUser) {
                this.setProfileData(currentUser);
                console.log('✅ User data loaded from authState:', currentUser.name);
            } else {
                console.warn('⚠️ No current user found');
            }
        } else {
            console.warn('⚠️ authState not available, loading from localStorage directly');
            this.loadFromLocalStorage();
        }
    }

    // Проверка доступности authState
    isAuthStateAvailable() {
        return window.authState && 
               typeof window.authState.getCurrentUser === 'function' &&
               typeof window.authState.updateUserProfile === 'function';
    }

    // Безопасное получение пользователя
    getCurrentUser() {
        if (this.isAuthStateAvailable()) {
            return window.authState.getCurrentUser();
        } else {
            // Fallback: загружаем напрямую из localStorage
            try {
                const userData = localStorage.getItem('fashioneco_current_user');
                return userData ? JSON.parse(userData) : null;
            } catch (error) {
                console.error('Error loading user from localStorage:', error);
                return null;
            }
        }
    }

    // Загрузка из localStorage
    loadFromLocalStorage() {
        try {
            const userData = localStorage.getItem('fashioneco_current_user');
            if (userData) {
                const user = JSON.parse(userData);
                this.setProfileData(user);
                console.log('✅ User data loaded from localStorage');
            }
        } catch (error) {
            console.error('Error loading from localStorage:', error);
        }
    }

    attachEventListeners() {
        console.log('🔧 Attaching event listeners...');

        // Обработчики для кнопок редактирования полей
        this.elements.editButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                const fieldId = event.target.getAttribute('data-field');
                console.log('✏️ Edit button clicked for:', fieldId);
                if (fieldId) {
                    this.enableEditing(fieldId);
                }
            });
        });

        // Обработчик отмены редактирования
        if (this.elements.cancelBtn) {
            this.elements.cancelBtn.addEventListener('click', () => {
                console.log('❌ Cancel button clicked');
                this.cancelEditing();
            });
        }

        // Обработчик сохранения формы
        this.elements.profileForm.addEventListener('submit', (event) => {
            event.preventDefault();
            console.log('💾 Save form submitted');
            this.saveProfile();
        });

        // Обработчик кнопки "Назад"
        if (this.elements.backBtn) {
            this.elements.backBtn.addEventListener('click', () => {
                console.log('⬅️ Back button clicked');
                this.handleBackButton();
            });
        }

        // Обработчики для аватара
        if (this.elements.userAvatar) {
            this.elements.userAvatar.addEventListener('click', () => {
                console.log('🖼️ Avatar clicked');
                this.elements.avatarInput.click();
            });
        }

        if (this.elements.changeAvatarBtn) {
            this.elements.changeAvatarBtn.addEventListener('click', () => {
                console.log('📷 Change avatar button clicked');
                this.elements.avatarInput.click();
            });
        }

        // Обработчик загрузки файла
        this.elements.avatarInput.addEventListener('change', (event) => {
            console.log('📁 File selected');
            this.handleAvatarUpload(event);
        });

        // Обработчик удаления аватара
        if (this.elements.removeAvatarBtn) {
            this.elements.removeAvatarBtn.addEventListener('click', () => {
                console.log('🗑️ Remove avatar clicked');
                this.removeAvatar();
            });
        }

        console.log('✅ All event listeners attached');
    }

    async handleAvatarUpload(event) {
    const fileInput = event.target;
    if (!fileInput.files || fileInput.files.length === 0) {
        return;
    }

    const file = fileInput.files[0];
    console.log('📤 Uploading file:', file.name, file.size, 'bytes');

    // Проверка типа файла
    if (!file.type.startsWith('image/')) {
        this.showErrorMessage('Пожалуйста, выберите файл изображения (JPEG, PNG, etc.)');
        return;
    }

    // Проверка размера файла (макс. 5MB)
    if (file.size > 5 * 1024 * 1024) {
        this.showErrorMessage('Размер файла не должен превышать 5MB');
        return;
    }

    try {
        this.showLoading('Загрузка фото...');

        // Чтение файла и создание URL
        const imageUrl = await this.readFileAsDataURL(file);
        this.setAvatarImage(imageUrl);
        this.hasCustomAvatar = true;
        
        // Сохраняем аватар через API
        if (this.isAuthStateAvailable()) {
            await window.authState.updateUserAvatar(imageUrl);
        } else {
            // Fallback: сохраняем в localStorage
            await this.saveAvatarToLocalStorage(imageUrl);
        }
        
        this.hideLoading();
        this.showSuccessMessage('Фото профиля успешно обновлено и сохранено!');
    } catch (error) {
        this.hideLoading();
        console.error('Error uploading avatar:', error);
        this.showErrorMessage('Ошибка при загрузке фото: ' + error.message);
    }
}


    readFileAsDataURL(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                if (e.target && e.target.result) {
                    resolve(e.target.result);
                } else {
                    reject(new Error('Не удалось прочитать файл'));
                }
            };
            reader.onerror = () => reject(new Error('Ошибка чтения файла'));
            reader.readAsDataURL(file);
        });
    }

    // Сохранение аватара в localStorage (fallback)
    async saveAvatarToLocalStorage(avatarUrl) {
        return new Promise((resolve) => {
            setTimeout(() => {
                try {
                    const currentUser = this.getCurrentUser();
                    if (currentUser) {
                        currentUser.avatar = avatarUrl;
                        localStorage.setItem('fashioneco_current_user', JSON.stringify(currentUser));
                        console.log('✅ Avatar saved to localStorage');
                    }
                    resolve(true);
                } catch (error) {
                    console.error('Error saving avatar to localStorage:', error);
                    resolve(false);
                }
            }, 500);
        });
    }

    setAvatarImage(imageUrl) {
        console.log('🖼️ Setting avatar image');
        this.elements.avatarImage.src = imageUrl;
        this.elements.avatarImage.classList.remove('hidden');
        this.elements.avatarInitials.classList.add('hidden');
    }

    removeAvatar() {
        console.log('🗑️ Removing avatar');
        this.elements.avatarImage.src = '';
        this.elements.avatarImage.classList.add('hidden');
        this.elements.avatarInitials.classList.remove('hidden');
        this.hasCustomAvatar = false;
        this.updateAvatar();
        
        // Сохраняем изменения ГЛОБАЛЬНО
        if (this.isAuthStateAvailable()) {
            window.authState.updateUserAvatar(null);
        } else {
            this.saveAvatarToLocalStorage(null);
        }
        
        this.showSuccessMessage('Фото профиля удалено');
    }

    enableEditing(fieldId) {
        const field = document.getElementById(fieldId);
        if (!field) {
            console.error('Field not found:', fieldId);
            return;
        }

        console.log('🔓 Enabling editing for:', fieldId);

        // Сохраняем исходное значение
        this.originalValues[fieldId] = field.value;

        // Делаем поле редактируемым
        field.readOnly = false;
        field.focus();
        field.style.background = '#fff';
        field.style.border = '2px solid var(--primary-color)';
        field.style.borderRadius = '8px';

        // Показываем кнопку отмены
        if (this.elements.cancelBtn) {
            this.elements.cancelBtn.style.display = 'inline-block';
        }

        this.isEditing = true;
    }

    cancelEditing() {
        console.log('↩️ Canceling editing');

        // Восстанавливаем исходные значения
        for (const fieldId in this.originalValues) {
            const field = document.getElementById(fieldId);
            if (field) {
                field.value = this.originalValues[fieldId];
                field.readOnly = true;
                field.style.background = '';
                field.style.border = '';
            }
        }

        // Очищаем сохраненные значения
        this.originalValues = {};

        // Скрываем кнопку отмены
        if (this.elements.cancelBtn) {
            this.elements.cancelBtn.style.display = 'none';
        }

        this.isEditing = false;
    }

    async saveProfile() {
        console.log('💾 Saving profile...');

        // Показываем индикатор загрузки
        this.showLoading('Сохранение данных...');

        // Собираем данные формы
        const formData = {
            name: this.elements.userNameInput.value.trim(),
            email: this.elements.userEmailInput.value.trim(),
            phone: this.elements.userPhoneInput.value.trim(),
            avatar: this.hasCustomAvatar ? this.elements.avatarImage.src : null
        };

        console.log('📝 Form data to save:', formData);

        // Валидация данных
        if (!this.validateFormData(formData)) {
            this.hideLoading();
            return;
        }

        try {
            await this.saveProfileChanges(formData);

            // Блокируем поля после сохранения
            this.setFieldsReadOnly(true);

            // Скрываем кнопку отмены
            if (this.elements.cancelBtn) {
                this.elements.cancelBtn.style.display = 'none';
            }

            // Очищаем сохраненные значения
            this.originalValues = {};
            this.isEditing = false;

            this.hideLoading();
            // Показываем уведомление об успешном сохранении
            this.showSuccessMessage('Данные успешно сохранены!');
        } catch (error) {
            this.hideLoading();
            this.showErrorMessage('Ошибка при сохранении данных: ' + error.message);
            console.error('Save error:', error);
        }
    }

    async saveProfileChanges(formData = null) {
    try {
        const dataToSave = formData || {
            name: this.elements.userNameInput.value.trim(),
            email: this.elements.userEmailInput.value.trim(),
            phone: this.elements.userPhoneInput.value.trim(),
            avatar: this.hasCustomAvatar ? this.elements.avatarImage.src : null
        };

        console.log('💾 Saving profile data globally via API:', dataToSave);

        // Сохраняем через authState (который использует API)
        if (this.isAuthStateAvailable()) {
            const updatedUser = await window.authState.updateUserProfile(dataToSave);
            
            if (!updatedUser) {
                throw new Error('Не удалось сохранить данные в системе');
            }

            console.log('✅ Profile data saved via API');
        } else {
            // Fallback: сохраняем в localStorage
            await this.saveToLocalStorage(dataToSave);
            console.log('✅ Profile data saved to localStorage');
        }

        // Обновляем аватар
        this.updateAvatar();

        return true;

    } catch (error) {
        console.error('❌ Error in saveProfileChanges:', error);
        throw error;
    }
}

    // Сохранение в localStorage (fallback)
    async saveToLocalStorage(profileData) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                try {
                    const currentUser = this.getCurrentUser();
                    if (currentUser) {
                        const updatedUser = {
                            ...currentUser,
                            ...profileData,
                            updatedAt: new Date().toISOString()
                        };
                        
                        localStorage.setItem('fashioneco_current_user', JSON.stringify(updatedUser));
                        console.log('✅ User data saved to localStorage');
                        resolve(true);
                    } else {
                        reject(new Error('Пользователь не найден'));
                    }
                } catch (error) {
                    console.error('Error saving to localStorage:', error);
                    reject(error);
                }
            }, 1000);
        });
    }

    validateFormData(data) {
        console.log('🔍 Validating form data...');

        if (!data.name || !data.name.trim()) {
            this.showFieldError('user-name', 'Введите имя');
            return false;
        }

        if (data.name.trim().length < 2) {
            this.showFieldError('user-name', 'Имя должно содержать至少 2 символа');
            return false;
        }

        if (!data.email || !this.isValidEmail(data.email)) {
            this.showFieldError('user-email', 'Введите корректный email');
            return false;
        }

        if (!data.phone || !this.isValidPhone(data.phone)) {
            this.showFieldError('user-phone', 'Введите корректный номер телефона');
            return false;
        }

        console.log('✅ Form data is valid');
        return true;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidPhone(phone) {
        // Простая валидация телефона
        const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
        return phoneRegex.test(phone.replace(/\s/g, ''));
    }

    showFieldError(fieldId, message) {
        console.error('❌ Field error:', fieldId, message);
        const field = document.getElementById(fieldId);
        if (field) {
            // Временная подсветка ошибки
            field.style.boxShadow = '0 0 0 2px rgba(229, 62, 62, 0.5)';
            field.style.borderColor = '#e53e3e';
            
            setTimeout(() => {
                field.style.boxShadow = '';
                field.style.borderColor = '';
            }, 3000);
        }
        this.showErrorMessage(message);
    }

    updateAvatar() {
        const fullName = this.elements.userNameInput.value;
        const names = fullName.split(' ').filter(name => name.trim() !== '');
        let initials = '';

        if (names.length >= 2) {
            initials = names[0].charAt(0) + names[names.length - 1].charAt(0);
        } else if (names.length === 1) {
            initials = names[0].charAt(0);
        } else {
            initials = 'U'; // User
        }

        console.log('👤 Updating avatar initials:', initials);
        this.elements.avatarInitials.textContent = initials.toUpperCase();
    }

    setFieldsReadOnly(readonly) {
        const inputs = document.querySelectorAll('#profile-form .input');
        inputs.forEach(input => {
            input.readOnly = readonly;
            input.style.background = readonly ? 'var(--secondary-color)' : '#fff';
            input.style.border = readonly ? 'none' : '2px solid var(--primary-color)';
            input.style.borderRadius = readonly ? '9999px' : '8px';
        });
    }

    showLoading(message = 'Загрузка...') {
        // Создаем или находим элемент загрузки
        let loadingEl = document.getElementById('profile-loading');
        if (!loadingEl) {
            loadingEl = document.createElement('div');
            loadingEl.id = 'profile-loading';
            loadingEl.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 20px 30px;
                border-radius: 12px;
                z-index: 10000;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 10px;
            `;
            document.body.appendChild(loadingEl);
        }
        
        loadingEl.innerHTML = `
            <div style="width: 20px; height: 20px; border: 2px solid #fff; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
            ${message}
        `;
        
        // Добавляем анимацию
        const style = document.createElement('style');
        style.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
        
        loadingEl.style.display = 'flex';
    }

    hideLoading() {
        const loadingEl = document.getElementById('profile-loading');
        if (loadingEl) {
            loadingEl.style.display = 'none';
        }
    }

    showSuccessMessage(message) {
        console.log('✅ Success:', message);
        this.showNotification(message, 'success');
    }

    showErrorMessage(message) {
        console.error('❌ Error:', message);
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        const backgroundColor = type === 'success' ? '#4CAF50' : 
                              type === 'error' ? '#f44336' : '#2196F3';
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${backgroundColor};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 10000;
            font-weight: 500;
            max-width: 300px;
            animation: slideIn 0.3s ease-out;
        `;
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Анимация появления
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        // Автоматическое скрытие
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => {
                    if (notification.parentNode) {
                        document.body.removeChild(notification);
                    }
                }, 300);
            }
        }, 3000);
    }

    handleBackButton() {
        if (this.isEditing) {
            if (confirm('У вас есть несохраненные изменения. Вы уверены, что хотите выйти?')) {
                window.location.href = 'index.html';
            }
        } else {
            window.location.href = 'index.html';
        }
    }

    // Публичные методы для внешнего использования
    getProfileData() {
        return {
            name: this.elements.userNameInput.value,
            email: this.elements.userEmailInput.value,
            phone: this.elements.userPhoneInput.value,
            avatar: this.hasCustomAvatar ? this.elements.avatarImage.src : null
        };
    }

    setProfileData(data) {
        console.log('🔧 Setting profile data:', data);
        
        if (data.name) this.elements.userNameInput.value = data.name;
        if (data.email) this.elements.userEmailInput.value = data.email;
        if (data.phone) this.elements.userPhoneInput.value = data.phone;
        
        if (data.avatar) {
            this.setAvatarImage(data.avatar);
            this.hasCustomAvatar = true;
        } else {
            this.hasCustomAvatar = false;
            this.elements.avatarImage.classList.add('hidden');
            this.elements.avatarInitials.classList.remove('hidden');
        }
        
        this.updateAvatar();
        
        // Блокируем поля после загрузки
        this.setFieldsReadOnly(true);
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔧 Initializing UserProfile...');
    
    // Проверяем авторизацию
    if (!window.authState || !window.authState.isLoggedIn || !window.authState.isLoggedIn()) {
        console.log('❌ User not logged in, redirecting to login');
        alert('Пожалуйста, войдите в систему');
        window.location.href = 'login.html';
        return;
    }
    
    const userProfile = new UserProfile();
    window.userProfile = userProfile;
    
    console.log('✅ UserProfile initialized successfully');
});

// Добавляем глобальные функции для отладки
window.debugProfile = function() {
    console.log('=== PROFILE DEBUG INFO ===');
    console.log('UserProfile instance:', window.userProfile);
    console.log('AuthState:', window.authState);
    console.log('Current user:', window.authState?.getCurrentUser());
    console.log('All users in localStorage:', JSON.parse(localStorage.getItem('fashioneco_all_users') || '[]'));
    console.log('Current user in localStorage:', JSON.parse(localStorage.getItem('fashioneco_current_user') || 'null'));
    console.log('Form data:', {
        name: document.getElementById('user-name')?.value,
        email: document.getElementById('user-email')?.value,
        phone: document.getElementById('user-phone')?.value
    });
};