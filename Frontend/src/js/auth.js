// auth.js - УПРОЩЕННАЯ ВЕРСИЯ
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
        // Регистрация
        if (document.getElementById('btn-register')) {
            document.getElementById('btn-register').addEventListener('click', (e) => {
                e.preventDefault();
                this.handleRegistration();
            });
        }

        // Логин
        if (document.getElementById('btn-login')) {
            document.getElementById('btn-login').addEventListener('click', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }

        // Enter в формах
        this.setupEnterHandlers();
    }

    setupEnterHandlers() {
        const registerForm = document.querySelector('#screen-register .auth-card');
        const loginForm = document.querySelector('#screen-login .auth-card');
        
        if (registerForm) {
            registerForm.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.handleRegistration();
                }
            });
        }
        
        if (loginForm) {
            loginForm.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.handleLogin();
                }
            });
        }
    }

    async handleRegistration() {
        console.log('🔄 Starting registration...');
        
        const formData = this.getRegistrationFormData();
        const validation = this.validateRegistrationForm(formData);
        
        if (!validation.isValid) {
            this.showFieldErrors(validation.errors);
            return;
        }

        try {
            this.showLoading('Регистрация...');
            await authState.register(formData);
            this.hideLoading();
            this.showSuccess('Регистрация прошла успешно!');
            
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1500);
            
        } catch (error) {
            this.hideLoading();
            this.handleAuthError(error, 'registration');
        }
    }

    async handleLogin() {
        console.log('🔄 Starting login...');
        
        const formData = this.getLoginFormData();
        const validation = this.validateLoginForm(formData);
        
        if (!validation.isValid) {
            this.showFieldErrors(validation.errors);
            return;
        }

        try {
            this.showLoading('Вход в систему...');
            await authState.login(formData.email, formData.password);
            this.hideLoading();
            this.showSuccess('Вход выполнен успешно!');
            
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1500);
            
        } catch (error) {
            this.hideLoading();
            this.handleAuthError(error, 'login');
        }
    }

    // Валидация
    validateRegistrationForm(formData) {
        const errors = {};
        
        if (!formData.name || formData.name.trim().length < 2) {
            errors.name = 'Имя должно содержать至少 2 символа';
        }

        if (!formData.email) {
            errors.email = 'Введите email';
        } else if (!this.isValidEmail(formData.email)) {
            errors.email = 'Введите корректный email';
        }

        if (!formData.password) {
            errors.password = 'Введите пароль';
        } else if (formData.password.length < 8) {
            errors.password = 'Пароль должен содержать至少 8 символов';
        }

        if (!formData.passwordConfirm) {
            errors.passwordConfirm = 'Подтвердите пароль';
        } else if (formData.password !== formData.passwordConfirm) {
            errors.passwordConfirm = 'Пароли не совпадают';
        }

        if (!formData.terms) {
            errors.terms = 'Необходимо принять условия использования';
        }

        return { isValid: Object.keys(errors).length === 0, errors };
    }

    validateLoginForm(formData) {
        const errors = {};
        
        if (!formData.email) {
            errors.email = 'Введите email';
        } else if (!this.isValidEmail(formData.email)) {
            errors.email = 'Введите корректный email';
        }

        if (!formData.password) {
            errors.password = 'Введите пароль';
        }

        return { isValid: Object.keys(errors).length === 0, errors };
    }

    // Утилиты
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
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

    // UI методы
    showFieldErrors(errors) {
        this.clearAllFieldErrors();
        
        for (const [fieldName, errorMessage] of Object.entries(errors)) {
            const field = document.getElementById(fieldName);
            if (field) {
                this.setFieldError(field, errorMessage);
            }
        }
    }

    setFieldError(field, message) {
        const fieldContainer = field.closest('.form-field');
        if (fieldContainer) {
            fieldContainer.classList.add('error');
            
            let errorElement = fieldContainer.querySelector('.error-message');
            if (!errorElement) {
                errorElement = document.createElement('div');
                errorElement.className = 'error-message';
                fieldContainer.appendChild(errorElement);
            }
            errorElement.textContent = message;
        }
    }

    clearAllFieldErrors() {
        const errorFields = document.querySelectorAll('.form-field.error');
        errorFields.forEach(field => {
            field.classList.remove('error');
            const errorElement = field.querySelector('.error-message');
            if (errorElement) {
                errorElement.style.display = 'none';
            }
        });
    }

    showLoading(message = 'Загрузка...') {
        // Реализация показа загрузки
        console.log('⏳ Loading:', message);
    }

    hideLoading() {
        // Реализация скрытия загрузки
        console.log('✅ Loading complete');
    }

    showSuccess(message) {
        alert('✅ ' + message);
    }

    showError(message) {
        alert('❌ ' + message);
    }

    handleAuthError(error, context) {
        console.error(`Auth error in ${context}:`, error);
        
        let userMessage = error.message || 'Произошла неизвестная ошибка';
        
        if (userMessage.includes('Email already registered')) {
            userMessage = 'Пользователь с таким email уже существует';
        } else if (userMessage.includes('Неверный email')) {
            userMessage = 'Неверный email или пароль';
        }
        
        this.showError(userMessage);
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Initializing AuthManager...');
    window.authManager = new AuthManager();
    console.log('✅ AuthManager ready');
});