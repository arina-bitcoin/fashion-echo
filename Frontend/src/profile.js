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
    }

    loadUserData() {
        // Загружаем данные из authState если пользователь авторизован
        if (this.isAuthStateAvailable()) {
            const currentUser = this.getCurrentUser();
            if (currentUser) {
                this.setProfileData(currentUser);
                console.log('✅ User data loaded from authState');
            }
        } else {
            console.warn('⚠️ authState not available, loading from localStorage directly');
            this.loadFromLocalStorage();
        }
    }

    // НОВЫЙ МЕТОД: Проверка доступности authState
    isAuthStateAvailable() {
        return window.authState && 
               typeof window.authState.getCurrentUser === 'function' &&
               typeof window.authState.saveUserToStorage === 'function';
    }

    // НОВЫЙ МЕТОД: Безопасное получение пользователя
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

    // НОВЫЙ МЕТОД: Безопасное сохранение пользователя
    saveUserToStorage(user) {
        if (this.isAuthStateAvailable()) {
            return window.authState.saveUserToStorage(user);
        } else {
            // Fallback: сохраняем напрямую в localStorage
            try {
                localStorage.setItem('fashioneco_current_user', JSON.stringify(user));
                return true;
            } catch (error) {
                console.error('Error saving user to localStorage:', error);
                return false;
            }
        }
    }

    // НОВЫЙ МЕТОД: Загрузка из localStorage
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
    }

    async handleAvatarUpload(event) {
        const fileInput = event.target;
        if (!fileInput.files || fileInput.files.length === 0) {
            return;
        }

        const file = fileInput.files[0];
        console.log('📤 Uploading file:', file.name);

        // Проверка типа файла
        if (!file.type.startsWith('image/')) {
            alert('Пожалуйста, выберите файл изображения');
            return;
        }

        // Проверка размера файла (макс. 5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('Размер файла не должен превышать 5MB');
            return;
        }

        try {
            // Чтение файла и создание URL
            const imageUrl = await this.readFileAsDataURL(file);
            this.setAvatarImage(imageUrl);
            this.hasCustomAvatar = true;
            
            // Сохраняем изменения сразу
            await this.saveProfileChanges();
            
            this.showSuccessMessage('Фото профиля успешно обновлено!');
        } catch (error) {
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
                    reject(new Error('Failed to read file'));
                }
            };
            reader.onerror = () => reject(new Error('File reading error'));
            reader.readAsDataURL(file);
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
        
        // Сохраняем изменения
        this.saveProfileChanges();
        
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
        field.style.border = '1px solid var(--primary-color)';

        // Показываем кнопку отмены
        if (this.elements.cancelBtn) {
            this.elements.cancelBtn.style.display = 'block';
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

        // Собираем данные формы
        const formData = {
            name: this.elements.userNameInput.value,
            email: this.elements.userEmailInput.value,
            phone: this.elements.userPhoneInput.value,
            avatar: this.hasCustomAvatar ? this.elements.avatarImage.src : null
        };

        console.log('📝 Form data to save:', formData);

        // Валидация данных
        if (!this.validateFormData(formData)) {
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

            // Показываем уведомление об успешном сохранении
            this.showSuccessMessage('Данные успешно сохранены!');
        } catch (error) {
            this.showErrorMessage('Ошибка при сохранении данных: ' + error.message);
            console.error('Save error:', error);
        }
    }

    async saveProfileChanges(formData = null) {
        try {
            // Если данные не переданы, собираем их из формы
            const dataToSave = formData || {
                name: this.elements.userNameInput.value,
                email: this.elements.userEmailInput.value,
                phone: this.elements.userPhoneInput.value,
                avatar: this.hasCustomAvatar ? this.elements.avatarImage.src : null
            };

            console.log('💾 Saving profile data:', dataToSave);

            // Получаем текущего пользователя безопасным способом
            const currentUser = this.getCurrentUser();
            console.log('👤 Current user before update:', currentUser);

            if (!currentUser) {
                throw new Error('Пользователь не найден');
            }

            // Обновляем данные
            const updatedUser = {
                ...currentUser,
                ...dataToSave,
                // Сохраняем системные поля
                registeredAt: currentUser.registeredAt || new Date().toISOString(),
                lastLogin: currentUser.lastLogin || new Date().toISOString()
            };

            console.log('🔄 Updated user data:', updatedUser);

            // Сохраняем безопасным способом
            const success = this.saveUserToStorage(updatedUser);
            
            if (!success) {
                throw new Error('Не удалось сохранить данные');
            }

            console.log('✅ Data saved successfully');
            
            // Обновляем аватар
            this.updateAvatar();

            return true;

        } catch (error) {
            console.error('❌ Error in saveProfileChanges:', error);
            throw error;
        }
    }

    validateFormData(data) {
        console.log('🔍 Validating form data...');

        if (!data.name || !data.name.trim()) {
            this.showFieldError('user-name', 'Введите имя');
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
            field.style.boxShadow = '0 0 0 2px rgba(229, 62, 62, 0.5)';
            setTimeout(() => {
                field.style.boxShadow = '';
            }, 3000);
        }
        alert(message);
    }

    updateAvatar() {
        const fullName = this.elements.userNameInput.value;
        const names = fullName.split(' ');
        let initials = '';

        if (names.length >= 2) {
            initials = names[0].charAt(0) + names[1].charAt(0);
        } else if (names.length === 1) {
            initials = names[0].charAt(0);
        }

        console.log('👤 Updating avatar initials:', initials);
        this.elements.avatarInitials.textContent = initials.toUpperCase();
    }

    setFieldsReadOnly(readonly) {
        const inputs = document.querySelectorAll('.input');
        inputs.forEach(input => {
            input.readOnly = readonly;
            input.style.background = readonly ? '' : '#fff';
            input.style.border = readonly ? '' : '1px solid var(--primary-color)';
        });
    }

    showSuccessMessage(message) {
        console.log('✅ Success:', message);
        alert('✅ ' + message);
    }

    showErrorMessage(message) {
        console.error('❌ Error:', message);
        alert('❌ ' + message);
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
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔧 Initializing UserProfile...');
    
    // Проверяем авторизацию перед инициализацией
    const userProfile = new UserProfile();
    window.userProfile = userProfile;
});