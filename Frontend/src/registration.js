// TypeScript-like implementation with type annotations in comments
        // This would be the compiled JavaScript from TypeScript
        
        // Type definitions (would be in .d.ts files in a real TypeScript project)
        /*
        interface User {
            name: string;
            email: string;
            phone: string;
            password: string;
        }
        
        interface ValidationResult {
            isValid: boolean;
            errors: Record<string, string>;
        }
        */
        
        // DOM Elements
        const screens = {
            login: document.getElementById('screen-login'),
            register: document.getElementById('screen-register'),
            map: document.getElementById('screen-map'),
            offers: document.getElementById('screen-offers')
        };
        
        const navigationButtons = {
            goRegister: document.getElementById('go-register'),
            goLogin: document.getElementById('go-login'),
            toOffers: document.getElementById('to-offers'),
            toMap: document.getElementById('to-map'),
            openLogin: document.getElementById('open-login')
        };
        
        const formButtons = {
            register: document.getElementById('btn-register'),
            login: document.getElementById('btn-login')
        };
        
        // Utility functions with type annotations
        /**
         * Shows a specific screen and hides all others
         * @param {HTMLElement} screen - The screen element to show
         */
        function showScreen(screen) {
            // Hide all screens
            Object.values(screens).forEach(s => {
                if (s) s.classList.remove('active');
            });
            
            // Show target screen
            if (screen) screen.classList.add('active');
        }
        
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
                showScreen(screens.map);
            }
        }
        
        /**
         * Handles user login
         */
        function handleLogin() {
            if (validateLoginForm()) {
                // In a real app, this would send data to a server
                alert('Вход выполнен успешно!');
                showScreen(screens.map);
            }
        }
        
        /**
         * Populates offers screen with sample data
         */
        function populateOffers() {
            const offersContainer = document.getElementById('offers');
            if (!offersContainer) return;
            
            const sampleOffers = [
                { id: 1, name: 'Платье летнее', price: '1200 руб.' },
                { id: 2, name: 'Джинсы классические', price: '800 руб.' },
                { id: 3, name: 'Куртка кожаная', price: '2500 руб.' },
                { id: 4, name: 'Блузка офисная', price: '600 руб.' },
                { id: 5, name: 'Юбка миди', price: '900 руб.' },
                { id: 6, name: 'Свитер шерстяной', price: '1100 руб.' }
            ];
            
            sampleOffers.forEach(offer => {
                const offerElement = document.createElement('div');
                offerElement.className = 'offer';
                offerElement.style.background = 'var(--card-color)';
                offerElement.style.borderRadius = '12px';
                offerElement.style.overflow = 'hidden';
                offerElement.style.boxShadow = 'var(--shadow)';
                
                offerElement.innerHTML = `
                    <img src="https://via.placeholder.com/300x300/F3E4D3/4B0505?text=FASHIONECO" alt="${offer.name}" style="display:block; width:100%; aspect-ratio:1/1; object-fit:cover;">
                    <div style="padding:10px; font-weight:600; color:var(--primary-color);">${offer.name}<br><small>${offer.price}</small></div>
                `;
                
                offersContainer.appendChild(offerElement);
            });
        }
        
        // Initialize the application
        document.addEventListener('DOMContentLoaded', function() {
            // Set up navigation
            if (navigationButtons.goRegister) {
                navigationButtons.goRegister.addEventListener('click', (e) => {
                    e.preventDefault();
                    showScreen(screens.register);
                });
            }
            
            if (navigationButtons.goLogin) {
                navigationButtons.goLogin.addEventListener('click', (e) => {
                    e.preventDefault();
                    showScreen(screens.login);
                });
            }
            
            if (navigationButtons.toOffers) {
                navigationButtons.toOffers.addEventListener('click', () => {
                    showScreen(screens.offers);
                });
            }
            
            if (navigationButtons.toMap) {
                navigationButtons.toMap.addEventListener('click', () => {
                    showScreen(screens.map);
                });
            }
            
            if (navigationButtons.openLogin) {
                navigationButtons.openLogin.addEventListener('click', () => {
                    showScreen(screens.login);
                });
            }
            
            // Set up form submissions
            if (formButtons.register) {
                formButtons.register.addEventListener('click', handleRegistration);
            }
            
            if (formButtons.login) {
                formButtons.login.addEventListener('click', handleLogin);
            }
            
            // Populate offers screen
            populateOffers();
        });
