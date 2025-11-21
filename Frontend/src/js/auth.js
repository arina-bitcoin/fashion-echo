// auth.js - Полная версия с валидацией, обработкой ошибок и интеграцией
console.log('✅ auth.js loaded');

class AuthManager {
    constructor() {
        this.isInitialized = false;
        this.init();
    }

    init() {
        if (this.isInitialized) return;
        
        console.log('🔧 AuthManager initializing...');
        this.setupEventListeners();
        this.isInitialized = true;
        console.log('✅ AuthManager initialized');
    }

    setupEventListeners() {
        // Обработчики для страницы регистрации
        if (document.getElementById('btn-register')) {
            document.getElementById('btn-register').addEventListener('click', (e) => {
                e.preventDefault();
                this.handleRegistration();
            });

            // Обработчик Enter в форме регистрации
            const registerForm = document.querySelector('#screen-register .auth-card');
            if (registerForm) {
                registerForm.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        this.handleRegistration();
                    }
                });
            }
        }

        // Обработчики для страницы входа
        if (document.getElementById('btn-login')) {
            document.getElementById('btn-login').addEventListener('click', (e) => {
                e.preventDefault();
                this.handleLogin();
            });

            // Обработчик Enter в форме входа
            const loginForm = document.querySelector('#screen-login .auth-card');
            if (loginForm) {
                loginForm.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        this.handleLogin();
                    }
                });
            }
        }

        // Обработчики для реального времени валидации
        this.setupRealTimeValidation();
    }

    setupRealTimeValidation() {
        // Валидация email в реальном времени
        const emailInputs = document.querySelectorAll('input[type="email"]');
        emailInputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateEmail(input);
            });
        });

        // Валидация пароля в реальном времени
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validatePassword(input);
            });
        });

        // Валидация телефона в реальном времени
        const phoneInputs = document.querySelectorAll('input[type="tel"]');
        phoneInputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validatePhone(input);
            });
            
            // Форматирование номера телефона
            input.addEventListener('input', (e) => {
                this.formatPhoneNumber(e.target);
            });
        });

        // Валидация имени в реальном времени
        const nameInputs = document.querySelectorAll('input#reg-name');
        nameInputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateName(input);
            });
        });
    }

    // ==================== ОСНОВНЫЕ МЕТОДЫ ====================

    async handleRegistration() {
        console.log('🔄 Starting registration process...');
        
        const formData = this.getRegistrationFormData();
        
        // Валидация формы
        const validation = this.validateRegistrationForm(formData);
        if (!validation.isValid) {
            this.showFieldErrors(validation.errors);
            return;
        }

        try {
            this.showLoading('Регистрация...');
            
            // Регистрация через authState
            await authState.register(formData);
            
            this.hideLoading();
            this.showSuccess('Регистрация прошла успешно!');
            
            // Задержка перед редиректом
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1500);
            
        } catch (error) {
            this.hideLoading();
            this.handleAuthError(error, 'registration');
        }
    }

    async handleLogin() {
        console.log('🔄 Starting login process...');
        
        const formData = this.getLoginFormData();
        
        // Валидация формы
        const validation = this.validateLoginForm(formData);
        if (!validation.isValid) {
            this.showFieldErrors(validation.errors);
            return;
        }

        try {
            this.showLoading('Вход в систему...');
            
            // Авторизация через authState
            await authState.login(formData.email, formData.password);
            
            this.hideLoading();
            this.showSuccess('Вход выполнен успешно!');
            
            // Задержка перед редиректом
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1500);
            
        } catch (error) {
            this.hideLoading();
            this.handleAuthError(error, 'login');
        }
    }

    // ==================== ВАЛИДАЦИЯ ====================

    validateRegistrationForm(formData) {
        const errors = {};
        
        // Валидация имени
        if (!formData.name || formData.name.trim().length < 2) {
            errors.name = 'Имя должно содержать至少 2 символа';
        } else if (formData.name.trim().length > 50) {
            errors.name = 'Имя не должно превышать 50 символов';
        }

        // Валидация email
        if (!formData.email) {
            errors.email = 'Введите email';
        } else if (!this.isValidEmail(formData.email)) {
            errors.email = 'Введите корректный email';
        }

        // Валидация телефона
        if (formData.phone && !this.isValidPhone(formData.phone)) {
            errors.phone = 'Введите корректный номер телефона';
        }

        // Валидация пароля
        if (!formData.password) {
            errors.password = 'Введите пароль';
        } else if (!this.isValidPassword(formData.password)) {
            errors.password = 'Пароль должен содержать至少 6 символов';
        }

        // Валидация подтверждения пароля
        if (!formData.passwordConfirm) {
            errors.passwordConfirm = 'Подтвердите пароль';
        } else if (formData.password !== formData.passwordConfirm) {
            errors.passwordConfirm = 'Пароли не совпадают';
        }

        // Валидация согласия с условиями
        if (!formData.terms) {
            errors.terms = 'Необходимо принять условия использования';
        }

        return {
            isValid: Object.keys(errors).length === 0,
            errors: errors
        };
    }

    validateLoginForm(formData) {
        const errors = {};
        
        // Валидация email
        if (!formData.email) {
            errors.email = 'Введите email';
        } else if (!this.isValidEmail(formData.email)) {
            errors.email = 'Введите корректный email';
        }

        // Валидация пароля
        if (!formData.password) {
            errors.password = 'Введите пароль';
        }

        return {
            isValid: Object.keys(errors).length === 0,
            errors: errors
        };
    }

    // Валидация в реальном времени
    validateEmail(input) {
        const value = input.value.trim();
        if (!value) return true;
        
        if (!this.isValidEmail(value)) {
            this.setFieldError(input, 'Введите корректный email');
            return false;
        } else {
            this.clearFieldError(input);
            return true;
        }
    }

    validatePassword(input) {
        const value = input.value;
        if (!value) return true;
        
        if (!this.isValidPassword(value)) {
            this.setFieldError(input, 'Пароль должен содержать 8 символов');
            return false;
        } else {
            this.clearFieldError(input);
            return true;
        }
    }

    validatePhone(input) {
        const value = input.value.trim();
        if (!value) return true;
        
        if (!this.isValidPhone(value)) {
            this.setFieldError(input, 'Введите корректный номер телефона');
            return false;
        } else {
            this.clearFieldError(input);
            return true;
        }
    }

    validateName(input) {
        const value = input.value.trim();
        if (!value) return true;
        
        if (value.length < 2) {
            this.setFieldError(input, 'Имя должно содержать минимум 2 символа');
            return false;
        } else if (value.length > 50) {
            this.setFieldError(input, 'Имя не должно превышать 50 символов');
            return false;
        } else {
            this.clearFieldError(input);
            return true;
        }
    }

    // ==================== УТИЛИТЫ ====================

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidPassword(password) {
        return password && password.length >= 8;
    }

    isValidPhone(phone) {
        // Убираем все нецифровые символы кроме +
        const cleanPhone = phone.replace(/[^\d+]/g, '');
        return cleanPhone.length >= 10;
    }

    formatPhoneNumber(input) {
        let value = input.value.replace(/\D/g, '');
        
        if (value.startsWith('7') || value.startsWith('8')) {
            value = '+7' + value.substring(1);
        }
        
        if (value.length > 0) {
            // Форматирование: +7 (XXX) XXX-XX-XX
            let formatted = '+7 ';
            
            if (value.length > 2) {
                formatted += '(' + value.substring(2, 5);
            }
            if (value.length > 5) {
                formatted += ') ' + value.substring(5, 8);
            }
            if (value.length > 8) {
                formatted += '-' + value.substring(8, 10);
            }
            if (value.length > 10) {
                formatted += '-' + value.substring(10, 12);
            }
            
            input.value = formatted;
        }
    }

    getRegistrationFormData() {
        return {
            name: document.getElementById('reg-name')?.value || '',
            email: document.getElementById('reg-email')?.value || '',
            phone: document.getElementById('reg-phone')?.value || '',
            password: document.getElementById('reg-pass')?.value || '',
            passwordConfirm: document.getElementById('reg-pass-confirm')?.value || '',
            terms: document.getElementById('reg-terms')?.checked || false
        };
    }

    getLoginFormData() {
        return {
            email: document.getElementById('login-email')?.value || '',
            password: document.getElementById('login-pass')?.value || ''
        };
    }

    // ==================== UI МЕТОДЫ ====================

    setFieldError(field, message) {
        if (!field) return;
        
        const fieldContainer = field.closest('.form-field');
        if (fieldContainer) {
            fieldContainer.classList.add('error');
            
            // Создаем или обновляем сообщение об ошибке
            let errorElement = fieldContainer.querySelector('.error-message');
            if (!errorElement) {
                errorElement = document.createElement('div');
                errorElement.className = 'error-message';
                fieldContainer.appendChild(errorElement);
            }
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
        
        // Визуальное выделение поля
        field.style.borderColor = '#e53e3e';
        field.style.boxShadow = '0 0 0 2px rgba(229, 62, 62, 0.1)';
    }

    clearFieldError(field) {
        if (!field) return;
        
        const fieldContainer = field.closest('.form-field');
        if (fieldContainer) {
            fieldContainer.classList.remove('error');
            
            const errorElement = fieldContainer.querySelector('.error-message');
            if (errorElement) {
                errorElement.style.display = 'none';
            }
        }
        
        // Сбрасываем стили
        field.style.borderColor = '';
        field.style.boxShadow = '';
    }

    showFieldErrors(errors) {
        // Очищаем все предыдущие ошибки
        this.clearAllFieldErrors();
        
        // Показываем новые ошибки
        for (const [fieldName, errorMessage] of Object.entries(errors)) {
            const field = document.getElementById(fieldName);
            if (field) {
                this.setFieldError(field, errorMessage);
            }
        }
        
        // Прокручиваем к первой ошибке
        const firstErrorField = document.querySelector('.form-field.error');
        if (firstErrorField) {
            firstErrorField.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
        }
    }

    clearAllFieldErrors() {
        const errorFields = document.querySelectorAll('.form-field.error');
        errorFields.forEach(fieldContainer => {
            fieldContainer.classList.remove('error');
            const errorElement = fieldContainer.querySelector('.error-message');
            if (errorElement) {
                errorElement.style.display = 'none';
            }
        });
        
        // Сбрасываем стили всех полей
        const allInputs = document.querySelectorAll('.input');
        allInputs.forEach(input => {
            input.style.borderColor = '';
            input.style.boxShadow = '';
        });
    }

    showLoading(message = 'Загрузка...') {
        // Создаем элемент загрузки
        let loadingEl = document.getElementById('auth-loading');
        if (!loadingEl) {
            loadingEl = document.createElement('div');
            loadingEl.id = 'auth-loading';
            loadingEl.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.7);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                color: white;
                font-size: 1.1rem;
            `;
            document.body.appendChild(loadingEl);
        }
        
        loadingEl.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; gap: 15px;">
                <div style="width: 40px; height: 40px; border: 3px solid #fff; border-top: 3px solid transparent; border-radius: 50%; animation: auth-spin 1s linear infinite;"></div>
                <div>${message}</div>
            </div>
        `;
        
        // Добавляем анимацию
        const style = document.createElement('style');
        if (!document.getElementById('auth-spin-style')) {
            style.id = 'auth-spin-style';
            style.textContent = `
                @keyframes auth-spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
        
        loadingEl.style.display = 'flex';
    }

    hideLoading() {
        const loadingEl = document.getElementById('auth-loading');
        if (loadingEl) {
            loadingEl.style.display = 'none';
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
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
            z-index: 10001;
            font-weight: 500;
            max-width: 300px;
            animation: auth-slideIn 0.3s ease-out;
        `;
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Анимация появления
        const style = document.createElement('style');
        if (!document.getElementById('auth-animation-style')) {
            style.id = 'auth-animation-style';
            style.textContent = `
                @keyframes auth-slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes auth-slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
        
        // Автоматическое скрытие
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'auth-slideOut 0.3s ease-in';
                setTimeout(() => {
                    if (notification.parentNode) {
                        document.body.removeChild(notification);
                    }
                }, 300);
            }
        }, 3000);
    }

    handleAuthError(error, context) {
        console.error(`Auth error in ${context}:`, error);
        
        const errorMessage = error.message || 'Произошла неизвестная ошибка';
        
        // Специфичные сообщения для разных ошибок
        let userMessage = errorMessage;
        
        if (errorMessage.includes('email already exists') || errorMessage.includes('уже существует')) {
            userMessage = 'Пользователь с таким email уже существует';
        } else if (errorMessage.includes('invalid email or password') || errorMessage.includes('Неверный email')) {
            userMessage = 'Неверный email или пароль';
        } else if (errorMessage.includes('network') || errorMessage.includes('Network Error')) {
            userMessage = 'Ошибка сети. Проверьте подключение к интернету';
        }
        
        this.showError(userMessage);
        
        // Подсвечиваем проблемные поля
        if (context === 'registration' && errorMessage.includes('email')) {
            this.setFieldError(document.getElementById('reg-email'), userMessage);
        }
    }

    // ==================== СЛУЖЕБНЫЕ МЕТОДЫ ====================

    // Проверка сложности пароля
    checkPasswordStrength(password) {
        if (!password) return 'weak';
        
        let strength = 0;
        
        // Длина
        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;
        
        // Разнообразие символов
        if (/[a-z]/.test(password)) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^a-zA-Z0-9]/.test(password)) strength++;
        
        if (strength <= 2) return 'weak';
        if (strength <= 4) return 'medium';
        return 'strong';
    }

    // Генерация случайного пароля
    generateRandomPassword(length = 12) {
        const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
        let password = '';
        for (let i = 0; i < length; i++) {
            password += charset.charAt(Math.floor(Math.random() * charset.length));
        }
        return password;
    }

    // Сброс формы
    resetForm(formType) {
        if (formType === 'register') {
            document.getElementById('reg-name').value = '';
            document.getElementById('reg-email').value = '';
            document.getElementById('reg-phone').value = '';
            document.getElementById('reg-pass').value = '';
            document.getElementById('reg-pass-confirm').value = '';
            document.getElementById('reg-terms').checked = false;
        } else if (formType === 'login') {
            document.getElementById('login-email').value = '';
            document.getElementById('login-pass').value = '';
        }
        
        this.clearAllFieldErrors();
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Initializing AuthManager...');
    
    // Создаем глобальный экземпляр
    window.authManager = new AuthManager();
    
    console.log('✅ AuthManager ready');
});

// Глобальные функции для отладки
window.debugAuth = function() {
    console.log('=== AUTH DEBUG INFO ===');
    console.log('AuthManager:', window.authManager);
    console.log('AuthState:', window.authState);
    console.log('Current user:', window.authState?.getCurrentUser());
    console.log('All users:', window.authState?.getAllUsers?.() || []);
    console.log('Is logged in:', window.authState?.isLoggedIn?.() || false);
};

// Автозаполнение для тестирования (только в development)
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    document.addEventListener('DOMContentLoaded', function() {
        // Автозаполнение формы входа для тестирования
        const loginEmail = document.getElementById('login-email');
        const loginPass = document.getElementById('login-pass');
        
        // if (loginEmail && loginPass) {
        //     loginEmail.value = 'test@example.com';
        //     loginPass.value = '123456';
        // }
        
        // Автозаполнение формы регистрации для тестирования
        const regName = document.getElementById('reg-name');
        const regEmail = document.getElementById('reg-email');
        const regPhone = document.getElementById('reg-phone');
        const regPass = document.getElementById('reg-pass');
        const regPassConfirm = document.getElementById('reg-pass-confirm');
        const regTerms = document.getElementById('reg-terms');
        
        // if (regName && regEmail) {
        //     const timestamp = Date.now();
        //     regName.value = 'Тестовый Пользователь';
        //     regEmail.value = `test${timestamp}@example.com`;
        //     regPhone.value = '+7 (912) 345-67-89';
        //     regPass.value = '123456';
        //     regPassConfirm.value = '123456';
        //     regTerms.checked = true;
        // }
    });
}