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
        
        // Добавляем форматирование телефона в реальном времени на странице регистрации
        this.setupPhoneFormatting();
    }
    
    // Форматирование телефонного номера в российском формате (работает в реальном времени)
    formatPhoneNumber(phone) {
        if (!phone) return '+7';
        
        // Удаляем все нечисловые символы кроме +
        let cleaned = phone.replace(/[^\d+]/g, '');
        
        // Ограничиваем максимальную длину
        if (cleaned.length > 12) {
            cleaned = cleaned.substring(0, 12);
        }
        
        // Нормализуем начало номера
        if (cleaned.startsWith('8')) {
            // 8 заменяем на +7
            cleaned = '+7' + cleaned.substring(1);
        } else if (cleaned.startsWith('7') && !cleaned.startsWith('+7')) {
            // 7 в начале заменяем на +7
            cleaned = '+7' + cleaned.substring(1);
        } else if (!cleaned.startsWith('+')) {
            // Если нет + и есть цифры, добавляем +7
            if (cleaned.length > 0) {
                cleaned = '+7' + cleaned;
            } else {
                return '+7';
            }
        } else if (cleaned.startsWith('+') && !cleaned.startsWith('+7')) {
            // Если начинается с + но не +7, заменяем
            cleaned = '+7' + cleaned.substring(1);
        }
        
        // Ограничиваем длину после нормализации
        if (cleaned.length > 12) {
            cleaned = cleaned.substring(0, 12);
        }
        
        // Если пусто, возвращаем +7
        if (!cleaned || cleaned === '+') {
            return '+7';
        }
        
        // Форматируем по мере ввода: +7 (999) 123-45-67
        if (cleaned.startsWith('+7')) {
            const digits = cleaned.substring(2); // Цифры после +7
            let formatted = '+7';
            
            if (digits.length === 0) {
                return formatted;
            }
            
            // Добавляем первую часть: (999
            formatted += ' (' + digits.substring(0, 3);
            
            if (digits.length > 3) {
                formatted += ') ' + digits.substring(3, 6);
                
                if (digits.length > 6) {
                    formatted += '-' + digits.substring(6, 8);
                    
                    if (digits.length > 8) {
                        formatted += '-' + digits.substring(8, 10);
                    }
                }
            } else if (digits.length === 3) {
                formatted += ')';
            }
            
            return formatted;
        }
        
        return cleaned;
    }
    
    setupPhoneFormatting() {
        const phoneInput = document.getElementById('reg-phone');
        if (phoneInput) {
            phoneInput.addEventListener('input', (e) => {
                const input = e.target;
                const cursorPosition = input.selectionStart;
                const oldValue = input.value;
                
                const formatted = this.formatPhoneNumber(oldValue);
                
                if (formatted !== oldValue) {
                    input.value = formatted;
                    
                    // Восстанавливаем позицию курсора
                    setTimeout(() => {
                        let newPosition = cursorPosition;
                        const lengthDiff = formatted.length - oldValue.length;
                        if (lengthDiff > 0) {
                            newPosition += lengthDiff;
                        }
                        newPosition = Math.min(newPosition, formatted.length);
                        input.setSelectionRange(newPosition, newPosition);
                    }, 0);
                }
            });
            
            // Форматируем при вставке
            phoneInput.addEventListener('paste', (e) => {
                e.preventDefault();
                const pastedText = (e.clipboardData || window.clipboardData).getData('text');
                const formatted = this.formatPhoneNumber(pastedText);
                e.target.value = formatted;
            });
        }
        
        // Добавляем форматирование email (приведение к нижнему регистру)
        const emailInput = document.getElementById('reg-email');
        if (emailInput) {
            emailInput.addEventListener('blur', (e) => {
                const normalized = e.target.value.toLowerCase().trim();
                if (normalized !== e.target.value) {
                    e.target.value = normalized;
                }
            });
        }
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
            // При ошибке логина показываем ошибку в полях
            const errorMessage = error.message || '';
            if (errorMessage.includes('Incorrect email or password') || 
                errorMessage.includes('401') ||
                errorMessage.includes('Неверный')) {
                // Показываем ошибку в обоих полях для неверных учетных данных
                this.setFieldError(document.getElementById('login-email'), 'Неверный email или пароль');
                this.setFieldError(document.getElementById('login-pass'), 'Неверный email или пароль');
            } else {
                this.handleAuthError(error, 'login');
            }
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
            errorElement.style.display = 'block';
        }
    }

    clearAllFieldErrors() {
        const errorFields = document.querySelectorAll('.form-field.error');
        errorFields.forEach(field => {
            field.classList.remove('error');
            const errorElement = field.querySelector('.error-message');
            if (errorElement) {
                errorElement.style.display = 'none';
                errorElement.textContent = '';
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
        
        // Обработка различных типов ошибок
        if (userMessage.includes('Email already registered') || userMessage.includes('already registered')) {
            userMessage = 'Пользователь с таким email уже существует';
        } else if (userMessage.includes('Incorrect email or password') || 
                   userMessage.includes('Неверный email') ||
                   userMessage.includes('401')) {
            userMessage = 'Неверный email или пароль';
        } else if (userMessage.includes('Inactive user')) {
            userMessage = 'Аккаунт неактивен. Обратитесь к администратору';
        } else if (userMessage.includes('HTTP 401')) {
            userMessage = 'Неверный email или пароль';
        } else if (userMessage.includes('HTTP 400')) {
            userMessage = 'Ошибка при обработке запроса. Проверьте введенные данные';
        } else if (userMessage.includes('NetworkError') || userMessage.includes('Failed to fetch')) {
            userMessage = 'Ошибка подключения к серверу. Проверьте подключение к интернету';
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