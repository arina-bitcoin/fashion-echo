// auth.js - Восстановленная версия
console.log('✅ auth.js loaded');

// Функции валидации
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPassword(password) {
    return password && password.length >= 6;
}

function setFieldError(field, isError) {
    if (field && field.parentElement) {
        if (isError) {
            field.parentElement.classList.add('error');
        } else {
            field.parentElement.classList.remove('error');
        }
    }
}

// ВАЖНО: Упрощенная валидация для быстрого тестирования
function quickValidateForm(formType) {
    if (formType === 'register') {
        const name = document.getElementById('reg-name');
        const email = document.getElementById('reg-email');
        const password = document.getElementById('reg-pass');
        
        if (!name.value.trim()) {
            alert('Введите имя');
            return false;
        }
        if (!isValidEmail(email.value)) {
            alert('Введите корректный email');
            return false;
        }
        if (!isValidPassword(password.value)) {
            alert('Пароль должен быть не менее 6 символов');
            return false;
        }
        return true;
    } else if (formType === 'login') {
        const email = document.getElementById('login-email');
        const password = document.getElementById('login-pass');
        
        if (!isValidEmail(email.value)) {
            alert('Введите корректный email');
            return false;
        }
        if (!password.value) {
            alert('Введите пароль');
            return false;
        }
        return true;
    }
    return false;
}

// Обработчик регистрации
// В auth.js в функции handleRegistration:
function handleRegistration() {
    console.log('🔄 Starting registration...');
    
    if (quickValidateForm('register')) {
        const userData = {
            name: document.getElementById('reg-name').value,
            email: document.getElementById('reg-email').value,
            phone: document.getElementById('reg-phone').value || '+7 XXX XXX-XX-XX',
            avatar: null,
            registeredAt: new Date().toISOString(),
            lastLogin: new Date().toISOString()
        };

        console.log('📝 User data for registration:', userData);

        // Сохраняем пользователя
        if (typeof authState !== 'undefined') {
            console.log('✅ Using authState');
            authState.saveUserToStorage(userData);
        } else {
            console.log('⚠️ Using localStorage directly');
            localStorage.setItem('fashioneco_current_user', JSON.stringify(userData));
        }

        // Перенаправляем на главную
        console.log('🔄 Redirecting to index.html');
        window.location.href = 'index.html';
    }
}

// Обработчик входа
function handleLogin() {
    console.log('🔄 Starting login...');
    
    if (quickValidateForm('login')) {
        const email = document.getElementById('login-email').value;
        
        const userData = {
            name: "Тестовый Пользователь",
            email: email,
            phone: "+7 (912) 345-67-89",
            avatar: null,
            lastLogin: new Date().toISOString()
        };

        console.log('📝 User data for login:', userData);

        // Сохраняем пользователя
        if (typeof authState !== 'undefined') {
            console.log('✅ Using authState');
            authState.saveUserToStorage(userData);
        } else {
            console.log('⚠️ Using localStorage directly');
            localStorage.setItem('fashioneco_current_user', JSON.stringify(userData));
        }

        // Перенаправляем на главную
        console.log('🔄 Redirecting to index.html');
        window.location.href = 'index.html';
    }
}

// Инициализация обработчиков
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM loaded, setting up auth handlers...');
    
    const registerBtn = document.getElementById('btn-register');
    const loginBtn = document.getElementById('btn-login');
    
    console.log('Register button:', registerBtn);
    console.log('Login button:', loginBtn);
    
    if (registerBtn) {
        registerBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🎯 Register button clicked');
            handleRegistration();
        });
    }
    
    if (loginBtn) {
        loginBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🎯 Login button clicked');
            handleLogin();
        });
    }
    
    // Также добавляем обработчики для Enter в формах
    const registerForm = document.querySelector('#screen-register .auth-card');
    const loginForm = document.querySelector('#screen-login .auth-card');
    
    if (registerForm) {
        registerForm.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleRegistration();
            }
        });
    }
    
    if (loginForm) {
        loginForm.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleLogin();
            }
        });
    }
});
