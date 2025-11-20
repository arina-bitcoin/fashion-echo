// Utility functions with type annotations
/**
 * Validates email format
 * @param {string} email - Email to validate
 * @returns {boolean} - True if email is valid
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validates phone number (simple validation)
 * @param {string} phone - Phone number to validate
 * @returns {boolean} - True if phone is valid
 */
function isValidPhone(phone) {
    return phone.trim().length >= 5;
}

/**
 * Validates password strength
 * @param {string} password - Password to validate
 * @returns {boolean} - True if password meets requirements
 */
function isValidPassword(password) {
    return password && password.length >= 6;
}

/**
 * Sets error state for a form field
 * @param {HTMLElement} field - The form field element
 * @param {boolean} isError - Whether to show error state
 */
function setFieldError(field, isError) {
    if (field && field.parentElement) {
        if (isError) {
            field.parentElement.classList.add('error');
        } else {
            field.parentElement.classList.remove('error');
        }
    }
}

/**
 * Validates registration form
 * @returns {boolean} - True if form is valid
 */
function validateRegistrationForm() {
    let isValid = true;
    
    // Get form elements
    const name = document.getElementById('reg-name');
    const email = document.getElementById('reg-email');
    const phone = document.getElementById('reg-phone');
    const password = document.getElementById('reg-pass');
    const passwordConfirm = document.getElementById('reg-pass-confirm');
    const terms = document.getElementById('reg-terms');
    
    // Validate name
    if (!name.value.trim()) {
        setFieldError(name, true);
        isValid = false;
    } else {
        setFieldError(name, false);
    }
    
    // Validate email
    if (!isValidEmail(email.value)) {
        setFieldError(email, true);
        isValid = false;
    } else {
        setFieldError(email, false);
    }
    
    // Validate phone
    if (!isValidPhone(phone.value)) {
        setFieldError(phone, true);
        isValid = false;
    } else {
        setFieldError(phone, false);
    }
    
    // Validate password
    if (!isValidPassword(password.value)) {
        setFieldError(password, true);
        isValid = false;
    } else {
        setFieldError(password, false);
    }
    
    // Validate password confirmation
    if (password.value !== passwordConfirm.value) {
        setFieldError(passwordConfirm, true);
        isValid = false;
    } else {
        setFieldError(passwordConfirm, false);
    }
    
    // Validate terms acceptance
    if (!terms.checked) {
        setFieldError(terms, true);
        isValid = false;
    } else {
        setFieldError(terms, false);
    }
    
    return isValid;
}

/**
 * Validates login form
 * @returns {boolean} - True if form is valid
 */
function validateLoginForm() {
    let isValid = true;
    
    // Get form elements
    const email = document.getElementById('login-email');
    const password = document.getElementById('login-pass');
    
    // Validate email
    if (!isValidEmail(email.value)) {
        setFieldError(email, true);
        isValid = false;
    } else {
        setFieldError(email, false);
    }
    
    // Validate password
    if (!password.value) {
        setFieldError(password, true);
        isValid = false;
    } else {
        setFieldError(password, false);
    }
    
    return isValid;
}

/**
 * Handles user registration
 */
function handleRegistration() {
    if (validateRegistrationForm()) {
        // In a real app, this would send data to a server
        alert('Регистрация прошла успешно!');
        window.location.href = 'main.html';
    }
}

/**
 * Handles user login
 */
function handleLogin() {
    if (validateLoginForm()) {
        // In a real app, this would send data to a server
        alert('Вход выполнен успешно!');
        window.location.href = 'main1.html';
    }
}