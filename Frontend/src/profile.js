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

        this.initializeElements();
        this.attachEventListeners();
        this.updateAvatar();
    }

    initializeElements() {
        // Проверяем, что все элементы найдены
        for (const key in this.elements) {
            if (!this.elements[key]) {
                console.error(`Element not found: ${key}`);
            }
        }
    }

    attachEventListeners() {
        // Обработчики для кнопок редактирования полей
        this.elements.editButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                const fieldId = event.target.getAttribute('data-field');
                if (fieldId) {
                    this.enableEditing(fieldId);
                }
            });
        });

        // Обработчик отмены редактирования
        if (this.elements.cancelBtn) {
            this.elements.cancelBtn.addEventListener('click', () => {
                this.cancelEditing();
            });
        }

        // Обработчик сохранения формы
        this.elements.profileForm.addEventListener('submit', (event) => {
            event.preventDefault();
            this.saveProfile();
        });

        // Обработчик кнопки "Назад"
        this.elements.backBtn.addEventListener('click', () => {
            this.handleBackButton();
        });

        // Обработчики для аватара
        if (this.elements.userAvatar) {
            this.elements.userAvatar.addEventListener('click', () => {
                this.elements.avatarInput.click();
            });
        }

        this.elements.changeAvatarBtn.addEventListener('click', () => {
            this.elements.avatarInput.click();
        });

        // Обработчик загрузки файла
        this.elements.avatarInput.addEventListener('change', (event) => {
            this.handleAvatarUpload(event);
        });

        // Обработчик удаления аватара
        this.elements.removeAvatarBtn.addEventListener('click', () => {
            this.removeAvatar();
        });
    }

    async handleAvatarUpload(event) {
        const fileInput = event.target;
        if (!fileInput.files || fileInput.files.length === 0) {
            return;
        }

        const file = fileInput.files[0];

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
            this.showSuccessMessage('Фото профиля успешно обновлено!');
        } catch (error) {
            console.error('Error uploading avatar:', error);
            this.showErrorMessage('Ошибка при загрузке фото');
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
        this.elements.avatarImage.src = imageUrl;
        this.elements.avatarImage.classList.remove('hidden');
        this.elements.avatarInitials.classList.add('hidden');
    }

    removeAvatar() {
        this.elements.avatarImage.src = '';
        this.elements.avatarImage.classList.add('hidden');
        this.elements.avatarInitials.classList.remove('hidden');
        this.hasCustomAvatar = false;
        this.updateAvatar();
        this.showSuccessMessage('Фото профиля удалено');
    }

    enableEditing(fieldId) {
        const field = document.getElementById(fieldId);
        if (!field) return;

        // Сохраняем исходное значение
        this.originalValues[fieldId] = field.value;

        // Делаем поле редактируемым
        field.readOnly = false;
        field.focus();

        // Показываем кнопку отмены
        if (this.elements.cancelBtn) {
            this.elements.cancelBtn.style.display = 'block';
        }

        this.isEditing = true;
    }

    cancelEditing() {
        // Восстанавливаем исходные значения
        for (const fieldId in this.originalValues) {
            const field = document.getElementById(fieldId);
            if (field) {
                field.value = this.originalValues[fieldId];
                field.readOnly = true;
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
        // Собираем данные формы
        const formData = {
            name: this.elements.userNameInput.value,
            email: this.elements.userEmailInput.value,
            phone: this.elements.userPhoneInput.value,
            avatar: this.hasCustomAvatar ? this.elements.avatarImage.src : null
        };

        // Валидация данных
        if (!this.validateFormData(formData)) {
            return;
        }

        try {
            // В реальном приложении здесь был бы запрос к серверу
            await this.saveToServer(formData);

            // Обновляем аватар с инициалами, если нет кастомного фото
            if (!this.hasCustomAvatar) {
                this.updateAvatar();
            }

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
            this.showErrorMessage('Ошибка при сохранении данных');
            console.error('Save error:', error);
        }
    }

    validateFormData(data) {
        if (!data.name.trim()) {
            this.showFieldError('user-name', 'Введите имя');
            return false;
        }

        if (!this.isValidEmail(data.email)) {
            this.showFieldError('user-email', 'Введите корректный email');
            return false;
        }

        if (!this.isValidPhone(data.phone)) {
            this.showFieldError('user-phone', 'Введите корректный номер телефона');
            return false;
        }

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
        const field = document.getElementById(fieldId);
        if (field) {
            field.style.boxShadow = '0 0 0 2px rgba(229, 62, 62, 0.5)';
            setTimeout(() => {
                field.style.boxShadow = '';
            }, 3000);
        }
        alert(message);
    }

    saveToServer(data) {
        // Имитация запроса к серверу
        return new Promise((resolve) => {
            setTimeout(() => {
                console.log('Данные сохранены на сервер:', data);
                resolve(true);
            }, 1000);
        });
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

        this.elements.avatarInitials.textContent = initials.toUpperCase();
    }

    setFieldsReadOnly(readonly) {
        const inputs = document.querySelectorAll('.input');
        inputs.forEach(input => {
            input.readOnly = readonly;
        });
    }

    showSuccessMessage(message) {
        alert(message);
    }

    showErrorMessage(message) {
        alert(message);
    }

    handleBackButton() {
        if (this.isEditing) {
            if (confirm('У вас есть несохраненные изменения. Вы уверены, что хотите выйти?')) {
                window.history.back();
            }
        } else {
            window.history.back();
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
        if (data.name) this.elements.userNameInput.value = data.name;
        if (data.email) this.elements.userEmailInput.value = data.email;
        if (data.phone) this.elements.userPhoneInput.value = data.phone;
        
        if (data.avatar) {
            this.setAvatarImage(data.avatar);
            this.hasCustomAvatar = true;
        }
        
        this.updateAvatar();
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    const userProfile = new UserProfile();
    window.userProfile = userProfile;
});