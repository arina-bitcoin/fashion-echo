// // profile.js - Версия без проверки авторизации
// class UserProfile {
//     constructor() {
//         console.log('🔧 UserProfile constructor started');
        
//         try {
//             this.originalValues = {};
//             this.isEditing = false;
//             this.hasCustomAvatar = false;
            
//             this.elements = {
//                 profileForm: document.getElementById('profile-form'),
//                 editButtons: document.querySelectorAll('.edit-btn'),
//                 cancelBtn: document.getElementById('cancel-btn'),
//                 saveBtn: document.getElementById('save-btn'),
//                 backBtn: document.getElementById('back-btn'),
//                 userAvatar: document.getElementById('user-avatar'),
//                 avatarImage: document.getElementById('avatar-image'),
//                 avatarInitials: document.getElementById('avatar-initials'),
//                 avatarInput: document.getElementById('avatar-input'),
//                 changeAvatarBtn: document.getElementById('change-avatar-btn'),
//                 removeAvatarBtn: document.getElementById('remove-avatar-btn'),
//                 userNameInput: document.getElementById('user-name'),
//                 userEmailInput: document.getElementById('user-email'),
//                 userPhoneInput: document.getElementById('user-phone')
//             };

//             console.log('🔧 Elements initialized');
//             this.initializeElements();
//             this.attachEventListeners();
//             this.loadUserData();
            
//         } catch (error) {
//             console.error('❌ Error in UserProfile constructor:', error);
//             this.showErrorMessage('Ошибка инициализации профиля');
//         }
//     }

//     initializeElements() {
//         console.log('🔧 Initializing elements...');
        
//         // Проверяем обязательные элементы
//         const requiredElements = ['profileForm', 'userNameInput', 'userEmailInput', 'userPhoneInput'];
        
//         for (const key of requiredElements) {
//             if (!this.elements[key]) {
//                 console.error(`❌ Required element not found: ${key}`);
//             }
//         }
        
//         console.log('✅ Elements initialized');
//     }

//     // loadUserData() {
//     //     console.log('🔧 Loading user data...');
        
//     //     try {
//     //         let currentUser = null;
            
//     //         // Пробуем получить пользователя из authState
//     //         if (window.authState && typeof window.authState.getCurrentUser === 'function') {
//     //             currentUser = window.authState.getCurrentUser();
//     //             console.log('👤 User from authState:', currentUser);
//     //         }
            
//     //         // Если не получилось, пробуем localStorage
//     //         if (!currentUser) {
//     //             try {
//     //                 const userData = localStorage.getItem('fashioneco_current_user');
//     //                 if (userData) {
//     //                     currentUser = JSON.parse(userData);
//     //                     console.log('👤 User from localStorage:', currentUser);
//     //                 }
//     //             } catch (error) {
//     //                 console.error('Error parsing localStorage user:', error);
//     //             }
//     //         }
            
//     //         // Если все еще нет пользователя, создаем тестового
//     //         if (!currentUser) {
//     //             currentUser = this.createTestUser();
//     //             console.log('👤 Created test user:', currentUser);
//     //         }
            
//     //         this.setProfileData(currentUser);
//     //         console.log('✅ User data loaded');
            
//     //     } catch (error) {
//     //         console.error('❌ Error loading user data:', error);
//     //         this.setDefaultData();
//     //     }
//     // }
//     async loadUserData() {
//         console.log('🔧 Loading user data...');
        
//         try {
//             // Пробуем загрузить с сервера если пользователь авторизован
//             if (window.apiService && window.apiService.isAuthenticated()) {
//                 try {
//                     const userData = await window.apiService.getCurrentUser();
//                     console.log('👤 User data from server:', userData);
//                     this.setProfileData(userData);
//                     this.saveUserToLocalStorage(userData);
//                     console.log('✅ User data loaded from server');
//                     return;
//                 } catch (error) {
//                     console.error('❌ Error loading from server:', error);
//                 }
//             }
            
//             // Fallback на localStorage
//             this.loadLocalUserData();
            
//         } catch (error) {
//             console.error('❌ Error loading user data:', error);
//             this.setDefaultData();
//         }
//     }

//     loadLocalUserData() {
//         try {
//             const userData = localStorage.getItem('fashioneco_current_user');
//             if (userData) {
//                 const user = JSON.parse(userData);
//                 console.log('👤 User from localStorage:', user);
//                 this.setProfileData(user);
//             } else {
//                 this.createTestUser();
//             }
//         } catch (error) {
//             console.error('Error loading local user data:', error);
//             this.setDefaultData();
//         }
//     }


//     createTestUser() {
//         const testUser = {
//             name: 'Иван Иванов',
//             email: 'ivan@example.com',
//             phone: '+7 (999) 123-45-67',
//             avatar: null,
//             createdAt: new Date().toISOString()
//         };
        
//         // Сохраняем тестового пользователя в localStorage
//         // localStorage.setItem('fashioneco_current_user', JSON.stringify(testUser));
//         this.saveUserToLocalStorage(testUser);
//         this.setProfileData(testUser);
//         console.log('👤 Created test user');

//         return testUser;
//     }

//     setDefaultData() {
//         console.log('🔧 Setting default data');
//         if (this.elements.userNameInput) this.elements.userNameInput.value = 'Тестовый пользователь';
//         if (this.elements.userEmailInput) this.elements.userEmailInput.value = 'test@example.com';
//         if (this.elements.userPhoneInput) this.elements.userPhoneInput.value = '+7 (999) 999-99-99';
//         this.updateAvatar();
//     }

//     attachEventListeners() {
//         console.log('🔧 Attaching event listeners...');

//         try {
//             // Обработчики для кнопок редактирования полей
//             if (this.elements.editButtons && this.elements.editButtons.length > 0) {
//                 this.elements.editButtons.forEach(button => {
//                     button.addEventListener('click', (event) => {
//                         const fieldId = event.target.getAttribute('data-field');
//                         console.log('✏️ Edit button clicked for:', fieldId);
//                         if (fieldId) {
//                             this.enableEditing(fieldId);
//                         }
//                     });
//                 });
//             }

//             // Обработчик отмены редактирования
//             if (this.elements.cancelBtn) {
//                 this.elements.cancelBtn.addEventListener('click', () => {
//                     console.log('❌ Cancel button clicked');
//                     this.cancelEditing();
//                 });
//             }

//             // Обработчик сохранения формы
//             if (this.elements.profileForm) {
//                 this.elements.profileForm.addEventListener('submit', (event) => {
//                     event.preventDefault();
//                     console.log('💾 Save form submitted');
//                     this.saveProfile();
//                 });
//             }

//             // Обработчик кнопки "Назад"
//             if (this.elements.backBtn) {
//                 this.elements.backBtn.addEventListener('click', () => {
//                     console.log('⬅️ Back button clicked');
//                     this.handleBackButton();
//                 });
//             }

//             // Обработчики для аватара
//             if (this.elements.userAvatar) {
//                 this.elements.userAvatar.addEventListener('click', () => {
//                     console.log('🖼️ Avatar clicked');
//                     if (this.elements.avatarInput) {
//                         this.elements.avatarInput.click();
//                     }
//                 });
//             }

//             if (this.elements.changeAvatarBtn) {
//                 this.elements.changeAvatarBtn.addEventListener('click', () => {
//                     console.log('📷 Change avatar button clicked');
//                     if (this.elements.avatarInput) {
//                         this.elements.avatarInput.click();
//                     }
//                 });
//             }

//             // Обработчик загрузки файла
//             if (this.elements.avatarInput) {
//                 this.elements.avatarInput.addEventListener('change', (event) => {
//                     console.log('📁 File selected');
//                     this.handleAvatarUpload(event);
//                 });
//             }

//             // Обработчик удаления аватара
//             if (this.elements.removeAvatarBtn) {
//                 this.elements.removeAvatarBtn.addEventListener('click', () => {
//                     console.log('🗑️ Remove avatar clicked');
//                     this.removeAvatar();
//                 });
//             }

//             console.log('✅ All event listeners attached');
//         } catch (error) {
//             console.error('❌ Error attaching event listeners:', error);
//         }
//     }

//     async handleAvatarUpload(event) {
//         const fileInput = event.target;
//         if (!fileInput.files || fileInput.files.length === 0) {
//             return;
//         }

//         const file = fileInput.files[0];
//         console.log('📤 Uploading file:', file.name);

//         // Проверка типа файла
//         if (!file.type.startsWith('image/')) {
//             this.showErrorMessage('Пожалуйста, выберите файл изображения');
//             return;
//         }

//         // Проверка размера файла (макс. 5MB)
//         if (file.size > 5 * 1024 * 1024) {
//             this.showErrorMessage('Размер файла не должен превышать 5MB');
//             return;
//         }

//         // try {
//         //     this.showLoading('Загрузка фото...');

//         //     // Чтение файла и создание URL
//         //     const imageUrl = await this.readFileAsDataURL(file);
//         //     this.setAvatarImage(imageUrl);
//         //     this.hasCustomAvatar = true;
            
//         //     // Сохраняем аватар
//         //     await this.saveAvatarToLocalStorage(imageUrl);
            
//         //     this.hideLoading();
//         //     this.showSuccessMessage('Фото профиля успешно обновлено!');
//         // } catch (error) {
//         //     this.hideLoading();
//         //     console.error('Error uploading avatar:', error);
//         //     this.showErrorMessage('Ошибка при загрузке фото');
//         // }

//         try {
//             this.showLoading('Загрузка фото...');

//             let avatarUrl;
            
//             // Если пользователь авторизован, загружаем на сервер
//             if (window.apiService.isAuthenticated()) {
//                 const response = await window.apiService.uploadAvatar(file);
//                 console.log('✅ Avatar upload response:', response);
                
//                 avatarUrl = response.avatar_url || 
//                            (response.avatar ? `http://localhost:8000/static/${response.avatar}` : null);
//             } else {
//                 // Локальная загрузка (для демо)
//                 avatarUrl = await this.readFileAsDataURL(file);
//             }

//             if (avatarUrl) {
//                 this.setAvatarImage(avatarUrl);
//                 this.hasCustomAvatar = true;
                
//                 // Сохраняем в localStorage
//                 await this.saveAvatarToLocalStorage(avatarUrl);
                
//                 this.hideLoading();
//                 this.showSuccessMessage('Фото профиля успешно обновлено!');
//             }

//         } catch (error) {
//             this.hideLoading();
//             console.error('Error uploading avatar:', error);
//             this.showErrorMessage('Ошибка при загрузке фото: ' + error.message);
//         } finally {
//             // Сбрасываем input
//             fileInput.value = '';
//         }
//     }

//     readFileAsDataURL(file) {
//         return new Promise((resolve, reject) => {
//             const reader = new FileReader();
//             reader.onload = (e) => {
//                 if (e.target && e.target.result) {
//                     resolve(e.target.result);
//                 } else {
//                     reject(new Error('Не удалось прочитать файл'));
//                 }
//             };
//             reader.onerror = () => reject(new Error('Ошибка чтения файла'));
//             reader.readAsDataURL(file);
//         });
//     }

//     // async saveAvatarToLocalStorage(avatarUrl) {
//     //     return new Promise((resolve) => {
//     //         setTimeout(() => {
//     //             try {
//     //                 const userData = localStorage.getItem('fashioneco_current_user');
//     //                 if (userData) {
//     //                     const user = JSON.parse(userData);
//     //                     user.avatar = avatarUrl;
//     //                     localStorage.setItem('fashioneco_current_user', JSON.stringify(user));
//     //                     console.log('✅ Avatar saved to localStorage');
//     //                 }
//     //                 resolve(true);
//     //             } catch (error) {
//     //                 console.error('Error saving avatar to localStorage:', error);
//     //                 resolve(false);
//     //             }
//     //         }, 500);
//     //     });

//     async saveAvatarToLocalStorage(avatarUrl) {
//         try {
//             const userData = localStorage.getItem('fashioneco_current_user');
//             if (userData) {
//                 const user = JSON.parse(userData);
//                 user.avatar = avatarUrl;
//                 localStorage.setItem('fashioneco_current_user', JSON.stringify(user));
//                 console.log('✅ Avatar saved to localStorage');
//             }
//         } catch (error) {
//             console.error('Error saving avatar to localStorage:', error);
//         }
//     }
//     }

//     setAvatarImage(imageUrl) {
//         console.log('🖼️ Setting avatar image');
//         if (this.elements.avatarImage) {
//             this.elements.avatarImage.src = imageUrl;
//             this.elements.avatarImage.classList.remove('hidden');
//         }
//         if (this.elements.avatarInitials) {
//             this.elements.avatarInitials.classList.add('hidden');
//         }
//     }

//     // removeAvatar() {
//     //     console.log('🗑️ Removing avatar');
//     //     if (this.elements.avatarImage) {
//     //         this.elements.avatarImage.src = '';
//     //         this.elements.avatarImage.classList.add('hidden');
//     //     }
//     //     if (this.elements.avatarInitials) {
//     //         this.elements.avatarInitials.classList.remove('hidden');
//     //     }
//     //     this.hasCustomAvatar = false;
//     //     this.updateAvatar();
        
//     //     this.saveAvatarToLocalStorage(null);
//     //     this.showSuccessMessage('Фото профиля удалено');
//     // }

//     async removeAvatar() {
//         console.log('🗑️ Removing avatar...');
        
//         try {
//             this.showLoading('Удаление фото...');
            
//             // Если пользователь авторизован, удаляем с сервера
//             if (window.apiService.isAuthenticated()) {
//                 await window.apiService.deleteAvatar();
//                 console.log('✅ Avatar deleted from server');
//             }
            
//             // Обновляем интерфейс
//             this.resetAvatarToDefault();
            
//             // Обновляем localStorage
//             await this.saveAvatarToLocalStorage(null);
            
//             this.hideLoading();
//             this.showSuccessMessage('Фото профиля удалено');
            
//         } catch (error) {
//             this.hideLoading();
//             console.error('Error deleting avatar:', error);
//             this.showErrorMessage('Ошибка при удалении фото: ' + error.message);
//         }
//     }

//     resetAvatarToDefault() {
//         console.log('🔄 Resetting avatar to default');
        
//         if (this.elements.avatarImage) {
//             this.elements.avatarImage.src = '';
//             this.elements.avatarImage.classList.add('hidden');
//         }
//         if (this.elements.avatarInitials) {
//             this.elements.avatarInitials.classList.remove('hidden');
//         }
        
//         this.hasCustomAvatar = false;
//         this.updateAvatar();
//     }

//     enableEditing(fieldId) {
//         const field = document.getElementById(fieldId);
//         if (!field) {
//             console.error('Field not found:', fieldId);
//             return;
//         }

//         console.log('🔓 Enabling editing for:', fieldId);

//         // Сохраняем исходное значение
//         this.originalValues[fieldId] = field.value;

//         // Делаем поле редактируемым
//         field.readOnly = false;
//         field.focus();
//         field.style.background = '#fff';
//         field.style.border = '2px solid var(--primary-color)';
//         field.style.borderRadius = '8px';

//         // Показываем кнопку отмены
//         if (this.elements.cancelBtn) {
//             this.elements.cancelBtn.style.display = 'inline-block';
//         }

//         this.isEditing = true;
//     }

//     cancelEditing() {
//         console.log('↩️ Canceling editing');

//         // Восстанавливаем исходные значения
//         for (const fieldId in this.originalValues) {
//             const field = document.getElementById(fieldId);
//             if (field) {
//                 field.value = this.originalValues[fieldId];
//                 field.readOnly = true;
//                 field.style.background = '';
//                 field.style.border = '';
//             }
//         }

//         // Очищаем сохраненные значения
//         this.originalValues = {};

//         // Скрываем кнопку отмены
//         if (this.elements.cancelBtn) {
//             this.elements.cancelBtn.style.display = 'none';
//         }

//         this.isEditing = false;
//     }

//     async saveProfile() {
//         console.log('💾 Saving profile...');

//         try {
//             // Показываем индикатор загрузки
//             this.showLoading('Сохранение данных...');

//             // Собираем данные формы
//             const formData = {
//                 name: this.elements.userNameInput.value.trim(),
//                 email: this.elements.userEmailInput.value.trim(),
//                 phone: this.elements.userPhoneInput.value.trim(),
//                 avatar: this.hasCustomAvatar && this.elements.avatarImage ? this.elements.avatarImage.src : null
//             };

//             console.log('📝 Form data to save:', formData);

//             // Валидация данных
//             if (!this.validateFormData(formData)) {
//                 this.hideLoading();
//                 return;
//             }

//             await this.saveProfileChanges(formData);

//             // Блокируем поля после сохранения
//             this.setFieldsReadOnly(true);

//             // Скрываем кнопку отмены
//             if (this.elements.cancelBtn) {
//                 this.elements.cancelBtn.style.display = 'none';
//             }

//             // Очищаем сохраненные значения
//             this.originalValues = {};
//             this.isEditing = false;

//             this.hideLoading();
//             this.showSuccessMessage('Данные успешно сохранены!');
//         } catch (error) {
//             this.hideLoading();
//             this.showErrorMessage('Ошибка при сохранении данных: ' + error.message);
//             console.error('Save error:', error);
//         }
//     }

//     async saveProfileChanges(formData = null) {
//         try {
//             const dataToSave = formData || {
//                 name: this.elements.userNameInput.value.trim(),
//                 email: this.elements.userEmailInput.value.trim(),
//                 phone: this.elements.userPhoneInput.value.trim(),
//                 avatar: this.hasCustomAvatar && this.elements.avatarImage ? this.elements.avatarImage.src : null
//             };

//             console.log('💾 Saving profile data:', dataToSave);

//             // Сохраняем в localStorage
//             await this.saveToLocalStorage(dataToSave);
//             console.log('✅ Profile data saved');

//             // Обновляем аватар
//             this.updateAvatar();

//             return true;

//         } catch (error) {
//             console.error('❌ Error in saveProfileChanges:', error);
//             throw error;
//         }
//     }

//     // Сохранение в localStorage
//     async saveToLocalStorage(profileData) {
//         return new Promise((resolve, reject) => {
//             setTimeout(() => {
//                 try {
//                     const userData = localStorage.getItem('fashioneco_current_user');
//                     if (userData) {
//                         const user = JSON.parse(userData);
//                         const updatedUser = {
//                             ...user,
//                             ...profileData,
//                             updatedAt: new Date().toISOString()
//                         };
                        
//                         localStorage.setItem('fashioneco_current_user', JSON.stringify(updatedUser));
//                         console.log('✅ User data saved to localStorage');
//                         resolve(true);
//                     } else {
//                         // Создаем нового пользователя если нет
//                         const newUser = {
//                             ...profileData,
//                             createdAt: new Date().toISOString(),
//                             updatedAt: new Date().toISOString()
//                         };
//                         localStorage.setItem('fashioneco_current_user', JSON.stringify(newUser));
//                         console.log('✅ New user created in localStorage');
//                         resolve(true);
//                     }
//                 } catch (error) {
//                     console.error('Error saving to localStorage:', error);
//                     reject(error);
//                 }
//             }, 1000);
//         });
//     }

//     validateFormData(data) {
//         console.log('🔍 Validating form data...');

//         if (!data.name || !data.name.trim()) {
//             this.showFieldError('user-name', 'Введите имя');
//             return false;
//         }

//         if (data.name.trim().length < 2) {
//             this.showFieldError('user-name', 'Имя должно содержать至少 2 символа');
//             return false;
//         }

//         if (!data.email || !this.isValidEmail(data.email)) {
//             this.showFieldError('user-email', 'Введите корректный email');
//             return false;
//         }

//         if (!data.phone || !this.isValidPhone(data.phone)) {
//             this.showFieldError('user-phone', 'Введите корректный номер телефона');
//             return false;
//         }

//         console.log('✅ Form data is valid');
//         return true;
//     }

//     isValidEmail(email) {
//         const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
//         return emailRegex.test(email);
//     }

//     isValidPhone(phone) {
//         const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
//         return phoneRegex.test(phone.replace(/\s/g, ''));
//     }

//     showFieldError(fieldId, message) {
//         console.error('❌ Field error:', fieldId, message);
//         const field = document.getElementById(fieldId);
//         if (field) {
//             field.style.boxShadow = '0 0 0 2px rgba(229, 62, 62, 0.5)';
//             field.style.borderColor = '#e53e3e';
            
//             setTimeout(() => {
//                 field.style.boxShadow = '';
//                 field.style.borderColor = '';
//             }, 3000);
//         }
//         this.showErrorMessage(message);
//     }

//     updateAvatar() {
//         const fullName = this.elements.userNameInput.value;
//         const names = fullName.split(' ').filter(name => name.trim() !== '');
//         let initials = '';

//         if (names.length >= 2) {
//             initials = names[0].charAt(0) + names[names.length - 1].charAt(0);
//         } else if (names.length === 1) {
//             initials = names[0].charAt(0);
//         } else {
//             initials = 'U';
//         }

//         console.log('👤 Updating avatar initials:', initials);
//         if (this.elements.avatarInitials) {
//             this.elements.avatarInitials.textContent = initials.toUpperCase();
//         }
//     }

//     setFieldsReadOnly(readonly) {
//         const inputs = document.querySelectorAll('#profile-form .input');
//         inputs.forEach(input => {
//             input.readOnly = readonly;
//             input.style.background = readonly ? 'var(--secondary-color)' : '#fff';
//             input.style.border = readonly ? 'none' : '2px solid var(--primary-color)';
//             input.style.borderRadius = readonly ? '9999px' : '8px';
//         });
//     }

//     showLoading(message = 'Загрузка...') {
//         let loadingEl = document.getElementById('profile-loading');
//         if (!loadingEl) {
//             loadingEl = document.createElement('div');
//             loadingEl.id = 'profile-loading';
//             loadingEl.style.cssText = `
//                 position: fixed;
//                 top: 50%;
//                 left: 50%;
//                 transform: translate(-50%, -50%);
//                 background: rgba(0,0,0,0.8);
//                 color: white;
//                 padding: 20px 30px;
//                 border-radius: 12px;
//                 z-index: 10000;
//                 font-weight: 500;
//                 display: flex;
//                 align-items: center;
//                 gap: 10px;
//             `;
//             document.body.appendChild(loadingEl);
//         }
        
//         loadingEl.innerHTML = `
//             <div style="width: 20px; height: 20px; border: 2px solid #fff; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
//             ${message}
//         `;
        
//         const style = document.createElement('style');
//         style.textContent = `@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`;
//         document.head.appendChild(style);
        
//         loadingEl.style.display = 'flex';
//     }

//     hideLoading() {
//         const loadingEl = document.getElementById('profile-loading');
//         if (loadingEl) {
//             loadingEl.style.display = 'none';
//         }
//     }

//     showSuccessMessage(message) {
//         console.log('✅ Success:', message);
//         this.showNotification(message, 'success');
//     }

//     showErrorMessage(message) {
//         console.error('❌ Error:', message);
//         this.showNotification(message, 'error');
//     }

//     showNotification(message, type = 'info') {
//         const notification = document.createElement('div');
//         const backgroundColor = type === 'success' ? '#4CAF50' : 
//                               type === 'error' ? '#f44336' : '#2196F3';
        
//         notification.style.cssText = `
//             position: fixed;
//             top: 20px;
//             right: 20px;
//             background: ${backgroundColor};
//             color: white;
//             padding: 15px 20px;
//             border-radius: 8px;
//             box-shadow: 0 4px 12px rgba(0,0,0,0.2);
//             z-index: 10000;
//             font-weight: 500;
//             max-width: 300px;
//             animation: slideIn 0.3s ease-out;
//         `;
        
//         notification.textContent = message;
//         document.body.appendChild(notification);
        
//         const style = document.createElement('style');
//         style.textContent = `
//             @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
//             @keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
//         `;
//         document.head.appendChild(style);
        
//         setTimeout(() => {
//             if (notification.parentNode) {
//                 notification.style.animation = 'slideOut 0.3s ease-in';
//                 setTimeout(() => {
//                     if (notification.parentNode) {
//                         document.body.removeChild(notification);
//                     }
//                 }, 300);
//             }
//         }, 3000);
//     }

//     handleBackButton() {
//         if (this.isEditing) {
//             if (confirm('У вас есть несохраненные изменения. Вы уверены, что хотите выйти?')) {
//                 window.location.href = 'index.html';
//             }
//         } else {
//             window.location.href = 'index.html';
//         }
//     }

//     setProfileData(data) {
//         console.log('🔧 Setting profile data:', data);
        
//         if (data.name && this.elements.userNameInput) this.elements.userNameInput.value = data.name;
//         if (data.email && this.elements.userEmailInput) this.elements.userEmailInput.value = data.email;
//         if (data.phone && this.elements.userPhoneInput) this.elements.userPhoneInput.value = data.phone;
        
//         if (data.avatar && this.elements.avatarImage) {
//             this.setAvatarImage(data.avatar);
//             this.hasCustomAvatar = true;
//         } else {
//             this.hasCustomAvatar = false;
//             if (this.elements.avatarImage) {
//                 this.elements.avatarImage.classList.add('hidden');
//             }
//             if (this.elements.avatarInitials) {
//                 this.elements.avatarInitials.classList.remove('hidden');
//             }
//         }
        
//         this.updateAvatar();
//         this.setFieldsReadOnly(true);
//     }
// }

// // ВАЖНО: УБИРАЕМ ВСЮ ПРОВЕРКУ АВТОРИЗАЦИИ
// document.addEventListener('DOMContentLoaded', () => {
//     console.log('🔧 DOM Content Loaded - NO AUTH CHECK');
    
//     // Сразу создаем тестового пользователя если его нет
//     if (!localStorage.getItem('fashioneco_current_user')) {
//         const testUser = {
//             name: 'Тестовый Пользователь',
//             email: 'test@example.com',
//             phone: '+7 (999) 999-99-99',
//             avatar: null,
//             createdAt: new Date().toISOString()
//         };
//         localStorage.setItem('fashioneco_current_user', JSON.stringify(testUser));
//         console.log('✅ Test user created');
//     }

//     try {
//         const userProfile = new UserProfile();
//         window.userProfile = userProfile;
//         console.log('✅ UserProfile initialized successfully');
//     } catch (error) {
//         console.error('❌ Error initializing UserProfile:', error);
        
//         // Показываем ошибку на странице
//         const errorDiv = document.createElement('div');
//         errorDiv.style.cssText = `
//             position: fixed;
//             top: 50%;
//             left: 50%;
//             transform: translate(-50%, -50%);
//             background: #f8d7da;
//             color: #721c24;
//             padding: 20px;
//             border-radius: 8px;
//             border: 1px solid #f5c6cb;
//             text-align: center;
//             z-index: 10000;
//         `;
//         errorDiv.innerHTML = `
//             <h3>Ошибка загрузки профиля</h3>
//             <p>${error.message}</p>
//             <button onclick="location.reload()" style="margin-top: 10px; padding: 8px 16px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">
//                 Перезагрузить
//             </button>
//         `;
//         document.body.appendChild(errorDiv);
//     }
// });

// console.log('🔧 profile.js loaded - NO AUTHENTICATION CHECK');

// Frontend/profile.js - ФИНАЛЬНАЯ ВЕРСИЯ
class UserProfile {
    constructor() {
        console.log('🔧 UserProfile constructor started');
        
        try {
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

            console.log('🔧 Elements initialized');
            this.initializeElements();
            this.attachEventListeners();
            this.loadUserData();
            
        } catch (error) {
            console.error('❌ Error in UserProfile constructor:', error);
            this.showErrorMessage('Ошибка инициализации профиля');
        }
    }

    initializeElements() {
        console.log('🔧 Initializing elements...');
        
        const requiredElements = ['profileForm', 'userNameInput', 'userEmailInput', 'userPhoneInput'];
        
        for (const key of requiredElements) {
            if (!this.elements[key]) {
                console.error(`❌ Required element not found: ${key}`);
            }
        }
        
        console.log('✅ Elements initialized');
    }

    async loadUserData() {
        console.log('🔧 Loading user data...');
        
        try {
            // Пробуем загрузить с сервера если пользователь авторизован
            if (window.apiService && window.apiService.isAuthenticated()) {
                try {
                    const userData = await window.apiService.getCurrentUser();
                    console.log('👤 User data from server:', userData);
                    this.setProfileData(userData);
                    this.saveUserToLocalStorage(userData);
                    console.log('✅ User data loaded from server');
                    return;
                } catch (error) {
                    console.error('❌ Error loading from server:', error);
                }
            }
            
            // Fallback на localStorage
            this.loadLocalUserData();
            
        } catch (error) {
            console.error('❌ Error loading user data:', error);
            this.setDefaultData();
        }
    }

    loadLocalUserData() {
        try {
            const userData = localStorage.getItem('fashioneco_current_user');
            if (userData) {
                const user = JSON.parse(userData);
                console.log('👤 User from localStorage:', user);
                this.setProfileData(user);
            } else {
                this.createTestUser();
            }
        } catch (error) {
            console.error('Error loading local user data:', error);
            this.setDefaultData();
        }
    }

    createTestUser() {
        const testUser = {
            name: 'Иван Иванов',
            email: 'ivan@example.com',
            phone: '+7 (999) 123-45-67',
            avatar: null,
            createdAt: new Date().toISOString()
        };
        
        this.saveUserToLocalStorage(testUser);
        this.setProfileData(testUser);
        console.log('👤 Created test user');
        
        return testUser;
    }

    setDefaultData() {
        console.log('🔧 Setting default data');
        if (this.elements.userNameInput) this.elements.userNameInput.value = 'Тестовый пользователь';
        if (this.elements.userEmailInput) this.elements.userEmailInput.value = 'test@example.com';
        if (this.elements.userPhoneInput) this.elements.userPhoneInput.value = '+7 (999) 999-99-99';
        this.updateAvatar();
    }

    attachEventListeners() {
        console.log('🔧 Attaching event listeners...');

        try {
            // Обработчики для кнопок редактирования полей
            if (this.elements.editButtons && this.elements.editButtons.length > 0) {
                this.elements.editButtons.forEach(button => {
                    button.addEventListener('click', (event) => {
                        const fieldId = event.target.getAttribute('data-field');
                        console.log('✏️ Edit button clicked for:', fieldId);
                        if (fieldId) {
                            this.enableEditing(fieldId);
                        }
                    });
                });
            }

            // Обработчик отмены редактирования
            if (this.elements.cancelBtn) {
                this.elements.cancelBtn.addEventListener('click', () => {
                    console.log('❌ Cancel button clicked');
                    this.cancelEditing();
                });
            }

            // Обработчик сохранения формы
            if (this.elements.profileForm) {
                this.elements.profileForm.addEventListener('submit', (event) => {
                    event.preventDefault();
                    console.log('💾 Save form submitted');
                    this.saveProfile();
                });
            }

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
                    if (this.elements.avatarInput) {
                        this.elements.avatarInput.click();
                    }
                });
            }

            if (this.elements.changeAvatarBtn) {
                this.elements.changeAvatarBtn.addEventListener('click', () => {
                    console.log('📷 Change avatar button clicked');
                    if (this.elements.avatarInput) {
                        this.elements.avatarInput.click();
                    }
                });
            }

            // Обработчик загрузки файла
            if (this.elements.avatarInput) {
                this.elements.avatarInput.addEventListener('change', (event) => {
                    console.log('📁 File selected');
                    this.handleAvatarUpload(event);
                });
            }

            // Обработчик удаления аватара
            if (this.elements.removeAvatarBtn) {
                this.elements.removeAvatarBtn.addEventListener('click', () => {
                    console.log('🗑️ Remove avatar clicked');
                    this.removeAvatar();
                });
            }

            // Обработчик кнопки удаления аккаунта
            const deleteAccountBtn = document.getElementById('delete-account-btn');
            if (deleteAccountBtn) {
                deleteAccountBtn.addEventListener('click', () => {
                    console.log('🗑️ Delete account clicked');
                    this.deleteAccount();
                });
            }

            // Добавляем обработчики для автоматического форматирования телефона в реальном времени
            if (this.elements.userPhoneInput) {
                this.elements.userPhoneInput.addEventListener('input', (e) => {
                    const input = e.target;
                    const cursorPosition = input.selectionStart;
                    const oldValue = input.value;
                    
                    const formatted = this.formatPhoneNumber(oldValue);
                    
                    if (formatted !== oldValue) {
                        input.value = formatted;
                        
                        // Восстанавливаем позицию курсора после форматирования
                        setTimeout(() => {
                            let newPosition = cursorPosition;
                            const lengthDiff = formatted.length - oldValue.length;
                            
                            // Корректируем позицию с учетом добавленных символов форматирования
                            if (lengthDiff > 0) {
                                // Если были добавлены символы, сдвигаем курсор
                                newPosition += lengthDiff;
                            }
                            
                            // Ограничиваем позицию курсора
                            newPosition = Math.min(newPosition, formatted.length);
                            input.setSelectionRange(newPosition, newPosition);
                        }, 0);
                    }
                });
                
                // Также форматируем при вставке текста
                this.elements.userPhoneInput.addEventListener('paste', (e) => {
                    e.preventDefault();
                    const pastedText = (e.clipboardData || window.clipboardData).getData('text');
                    const formatted = this.formatPhoneNumber(pastedText);
                    e.target.value = formatted;
                });
            }

            if (this.elements.userEmailInput) {
                this.elements.userEmailInput.addEventListener('blur', (e) => {
                    // Приводим email к нижнему регистру при потере фокуса
                    const normalized = e.target.value.toLowerCase().trim();
                    if (normalized !== e.target.value) {
                        e.target.value = normalized;
                    }
                });
            }

            console.log('✅ All event listeners attached');
        } catch (error) {
            console.error('❌ Error attaching event listeners:', error);
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
            this.showErrorMessage('Пожалуйста, выберите файл изображения');
            return;
        }

        // Проверка размера файла (макс. 5MB)
        if (file.size > 5 * 1024 * 1024) {
            this.showErrorMessage('Размер файла не должен превышать 5MB');
            return;
        }

        try {
            this.showLoading('Загрузка фото...');

            let avatarUrl;
            let response = null; // ← СОЗДАЕМ ПЕРЕМЕННУЮ ЗДЕСЬ
            
            // Если пользователь авторизован, загружаем на сервер
            if (window.apiService.isAuthenticated()) {
                response = await window.apiService.uploadAvatar(file);
                console.log('✅ Avatar upload response:', response);
                
                // avatarUrl = response.avatar_url || 
                //            (response.avatar ? `http://localhost:8000/static/${response.avatar}` : null);
                // ИСПРАВЛЕННАЯ ОБРАБОТКА ОТВЕТА
                if (response.avatar_url) {
                    avatarUrl = response.avatar_url;
                } else if (response.avatar) {
                    // Конструируем правильный URL
                    // avatarUrl = `http://localhost:8000/static/${response.avatar}`;
                    const baseUrl = 'http://localhost:8000';
                    const avatarPath = response.avatar;
                    
                    // Убираем возможные дублирующие слеши
                    const cleanPath = avatarPath.startsWith('/') 
                        ? avatarPath.slice(1) 
                        : avatarPath;
                    
                // Собираем конечный URL
                avatarUrl = `${baseUrl}/static/${cleanPath}`;
                console.log('🔗 Constructed avatar URL:', avatarUrl);
                }
            } else {
                // Локальная загрузка (для демо)
                avatarUrl = await this.readFileAsDataURL(file);
            }

            if (avatarUrl) {
                // Проверяем доступность изображения перед установкой
                // const isValid = await this.checkImageUrl(avatarUrl);
                
                // if (isValid) {
                    this.setAvatarImage(avatarUrl);
                    this.hasCustomAvatar = true;
                    
                    // Используем response
                    const avatarForStorage = response?.avatar || avatarUrl;
                    await this.saveAvatarToLocalStorage(avatarForStorage);
                    
                    this.hideLoading();
                    this.showSuccessMessage('Фото профиля успешно обновлено!');
                // } else {
                //     this.hideLoading();
                //     this.showErrorMessage('Не удалось загрузить изображение. Проверьте URL.');
                //     console.error('Invalid image URL:', avatarUrl);
                // }
            // } else {
            //     this.hideLoading();
            //     this.showErrorMessage('Не удалось получить URL аватара');
            }

        } catch (error) {
            this.hideLoading();
            console.error('Error uploading avatar:', error);
            this.showErrorMessage('Ошибка при загрузке фото: ' + error.message);
        } finally {
            // Сбрасываем input
            fileInput.value = '';
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

    async saveAvatarToLocalStorage(avatarUrl) {
        try {
            const userData = localStorage.getItem('fashioneco_current_user');
            if (userData) {
                const user = JSON.parse(userData);
                user.avatar = avatarUrl;
                localStorage.setItem('fashioneco_current_user', JSON.stringify(user));
                console.log('✅ Avatar saved to localStorage');
            }
        } catch (error) {
            console.error('Error saving avatar to localStorage:', error);
        }
    }

    setAvatarImage(imageUrl) {
        console.log('🖼️ Setting avatar image:', imageUrl);
        if (this.elements.avatarImage) {
            this.elements.avatarImage.src = imageUrl;
            this.elements.avatarImage.classList.remove('hidden');
        }
        if (this.elements.avatarInitials) {
            this.elements.avatarInitials.classList.add('hidden');
        }
    }

    async removeAvatar() {
        console.log('🗑️ Removing avatar...');
        
        try {
            this.showLoading('Удаление фото...');
            
            // Если пользователь авторизован, удаляем с сервера
            if (window.apiService.isAuthenticated()) {
                await window.apiService.deleteAvatar();
                console.log('✅ Avatar deleted from server');
            }
            
            // Обновляем интерфейс
            this.resetAvatarToDefault();
            
            // Обновляем localStorage
            await this.saveAvatarToLocalStorage(null);
            
            this.hideLoading();
            this.showSuccessMessage('Фото профиля удалено');
            
        } catch (error) {
            this.hideLoading();
            console.error('Error deleting avatar:', error);
            this.showErrorMessage('Ошибка при удалении фото: ' + error.message);
        }
    }

    resetAvatarToDefault() {
        console.log('🔄 Resetting avatar to default');
        
        if (this.elements.avatarImage) {
            this.elements.avatarImage.src = '';
            this.elements.avatarImage.classList.add('hidden');
        }
        if (this.elements.avatarInitials) {
            this.elements.avatarInitials.classList.remove('hidden');
        }
        
        this.hasCustomAvatar = false;
        this.updateAvatar();
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

        try {
            this.showLoading('Сохранение данных...');

            // Собираем данные формы
            const formData = {
                name: this.elements.userNameInput.value.trim(),
                email: this.elements.userEmailInput.value.trim(),
                phone: this.elements.userPhoneInput.value.trim()
            };

            console.log('📝 Form data to save:', formData);

            // Валидация данных
            if (!this.validateFormData(formData)) {
                this.hideLoading();
                return;
            }

            // СРАЗУ обновляем поля в UI для более быстрого отклика
            // (данные уже валидированы)
            this.setProfileData(formData);
            this.setFieldsReadOnly(true);

            // Сохраняем на сервер или локально
            const savedData = await this.saveProfileChanges(formData);
            
            // Обновляем данные из ответа сервера (может отличаться от отправленных)
            if (savedData) {
                this.setProfileData(savedData);
            }

            // ВАЖНО: Обновляем originalValues новыми сохраненными значениями
            // чтобы cancelEditing не перезаписывал их
            if (this.elements.userNameInput) {
                this.originalValues['user-name'] = this.elements.userNameInput.value;
            }
            if (this.elements.userEmailInput) {
                this.originalValues['user-email'] = this.elements.userEmailInput.value;
            }
            if (this.elements.userPhoneInput) {
                this.originalValues['user-phone'] = this.elements.userPhoneInput.value;
            }

            // Блокируем поля после сохранения
            this.setFieldsReadOnly(true);
            
            // Очищаем состояние редактирования БЕЗ восстановления старых значений
            this.originalValues = {};
            this.isEditing = false;
            if (this.elements.cancelBtn) {
                this.elements.cancelBtn.style.display = 'none';
            }

            // ПРИНУДИТЕЛЬНО обновляем поля еще раз после всех операций
            // чтобы гарантировать, что новые данные отображаются
            if (savedData) {
                setTimeout(() => {
                    this.setProfileData(savedData);
                    console.log('🔄 Принудительное обновление данных');
                }, 100);
            }

            this.hideLoading();
            this.showSuccessMessage('Данные успешно сохранены!');
            
            // Дополнительная проверка: выводим текущие значения
            console.log('🔍 ДАННЫЕ ПОСЛЕ СОХРАНЕНИЯ:');
            console.log('   Имя:', this.elements.userNameInput?.value);
            console.log('   Email:', this.elements.userEmailInput?.value);
            console.log('   Телефон:', this.elements.userPhoneInput?.value);

        } catch (error) {
            this.hideLoading();
            this.showErrorMessage('Ошибка при сохранении данных: ' + error.message);
            console.error('Save error:', error);
        }
    }

    async saveProfileChanges(formData) {
    try {
        console.log('💾 Saving profile data:', formData);

        let updatedUserData;

        // Если пользователь авторизован, сохраняем на сервер
        if (window.apiService.isAuthenticated()) {
            const response = await window.apiService.updateProfile(formData);
            console.log('✅ Profile updated on server:', response);
            updatedUserData = response; // Сохраняем ответ сервера
        } else {
            // Локальное сохранение
            updatedUserData = formData;
        }

        // Сохраняем в localStorage
        await this.saveUserToLocalStorage(updatedUserData);
        console.log('✅ Profile data saved locally');

        // ВАЖНО: Обновляем данные в интерфейсе сразу после сохранения
        // Используем данные из ответа сервера или из formData
        const dataToDisplay = updatedUserData || formData;
        
        // Формируем данные для отображения (учитываем разные структуры ответа)
        const displayData = {
            name: dataToDisplay.name || formData.name || '',
            email: dataToDisplay.email || formData.email || '',
            phone: dataToDisplay.phone || formData.phone || '',
            avatar: dataToDisplay.avatar,
            avatar_url: dataToDisplay.avatar_url
        };
        
        console.log('📋 Data to display:', displayData);
        this.setProfileData(displayData);
        
        // Обновляем аватар (инициалы могут измениться)
        this.updateAvatar();
        
        // Убеждаемся, что поля заблокированы после сохранения
        this.setFieldsReadOnly(true);

        return displayData;

    } catch (error) {
        console.error('❌ Error in saveProfileChanges:', error);
        throw error;
    }
}

    async saveUserToLocalStorage(userData) {
        try {
            const existingData = localStorage.getItem('fashioneco_current_user');
            let user = existingData ? JSON.parse(existingData) : {};
            
            const updatedUser = {
                ...user,
                ...userData,
                updatedAt: new Date().toISOString()
            };
            
            localStorage.setItem('fashioneco_current_user', JSON.stringify(updatedUser));
            console.log('✅ User data saved to localStorage');
        } catch (error) {
            console.error('Error saving to localStorage:', error);
            throw error;
        }
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
        const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
        return phoneRegex.test(phone.replace(/\s/g, ''));
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

    showFieldError(fieldId, message) {
        console.error('❌ Field error:', fieldId, message);
        const field = document.getElementById(fieldId);
        if (field) {
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
        const fullName = this.elements.userNameInput ? this.elements.userNameInput.value : '';
        const names = fullName.split(' ').filter(name => name.trim() !== '');
        let initials = '';

        if (names.length >= 2) {
            initials = names[0].charAt(0) + names[names.length - 1].charAt(0);
        } else if (names.length === 1) {
            initials = names[0].charAt(0);
        } else {
            initials = 'U';
        }

        console.log('👤 Updating avatar initials:', initials);
        if (this.elements.avatarInitials) {
            this.elements.avatarInitials.textContent = initials.toUpperCase();
        }
    }

    setFieldsReadOnly(readonly) {
        const inputs = document.querySelectorAll('#profile-form .input');
        inputs.forEach(input => {
            input.readOnly = readonly;
            input.style.background = readonly ? 'var(--secondary-color)' : '#fff';
            input.style.border = readonly ? 'none' : '2px solid var(--primary-color)';
            // ИСПРАВЛЕНИЕ: Всегда делаем поля круглыми
            input.style.borderRadius = '9999px';
        });
    }

    showLoading(message = 'Загрузка...') {
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
        
        const style = document.createElement('style');
        if (!document.querySelector('#loading-styles')) {
            style.id = 'loading-styles';
            style.textContent = `@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`;
            document.head.appendChild(style);
        }
        
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
        // Удаляем существующие уведомления
        const existingNotifications = document.querySelectorAll('.profile-notification');
        existingNotifications.forEach(notification => notification.remove());

        const notification = document.createElement('div');
        const backgroundColor = type === 'success' ? '#4CAF50' : 
                              type === 'error' ? '#f44336' : '#2196F3';
        
        notification.className = 'profile-notification';
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
        
        // Добавляем стили только если их еще нет
        if (!document.querySelector('#notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
                @keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
            `;
            document.head.appendChild(style);
        }
        
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
                window.history.back();
            }
        } else {
            window.history.back();
        }
    }

    setProfileData(data) {
        console.log('🔧 Setting profile data:', data);
        
        // ИСПРАВЛЕНИЕ: Всегда обновляем поля формы, даже если значение пустое
        // Временно убираем readonly для обновления значений
        if (this.elements.userNameInput) {
            const wasReadonly = this.elements.userNameInput.readOnly;
            this.elements.userNameInput.readOnly = false;
            this.elements.userNameInput.value = data.name || '';
            this.elements.userNameInput.readOnly = wasReadonly;
            console.log('✅ Updated name field:', this.elements.userNameInput.value);
        }
        if (this.elements.userEmailInput) {
            // Форматируем email - приводим к нижнему регистру
            const formattedEmail = data.email ? data.email.toLowerCase().trim() : '';
            const wasReadonly = this.elements.userEmailInput.readOnly;
            this.elements.userEmailInput.readOnly = false;
            this.elements.userEmailInput.value = formattedEmail;
            this.elements.userEmailInput.readOnly = wasReadonly;
            console.log('✅ Updated email field:', this.elements.userEmailInput.value);
        }
        if (this.elements.userPhoneInput) {
            // Форматируем телефон
            const formattedPhone = data.phone ? this.formatPhoneNumber(data.phone) : '';
            const wasReadonly = this.elements.userPhoneInput.readOnly;
            this.elements.userPhoneInput.readOnly = false;
            this.elements.userPhoneInput.value = formattedPhone;
            this.elements.userPhoneInput.readOnly = wasReadonly;
            console.log('✅ Updated phone field:', this.elements.userPhoneInput.value);
        }
        
    //     // Обработка аватара
    //     if (data.avatar_url || data.avatar) {
    //         const avatarUrl = data.avatar_url || 
    //                         (data.avatar ? `http://localhost:8000/static/${data.avatar}` : data.avatar);
    //         this.setAvatarImage(avatarUrl);
    //         this.hasCustomAvatar = true;
    //     } else {
    //         this.resetAvatarToDefault();
    //     }
        
    //     // Обновляем инициалы аватара
    //     this.updateAvatar();
        
    //     // Блокируем поля после обновления
    //     this.setFieldsReadOnly(true);
        
    //     console.log('✅ Profile data applied to form');
    // }

    // Обработка аватара - ИСПРАВЛЕННАЯ ВЕРСИЯ
        if (data.avatar_url || data.avatar) {
            let avatarUrl;
            
            if (data.avatar_url) {
                // Если есть прямой URL
                avatarUrl = data.avatar_url;
            } else if (data.avatar) {
                // Если есть путь к файлу
                // Убедимся, что путь начинается правильно
                // const avatarPath = data.avatar.startsWith('images/') ? data.avatar : `images/avatars/${data.avatar}`;
                // avatarUrl = `http://localhost:8000/static/${avatarPath}`;
                const baseUrl = 'http://localhost:8000';
                const avatarPath = data.avatar;
                avatarUrl = `${baseUrl}/static/${avatarPath}`;
            }
            
            console.log('🖼️ Avatar URL:', avatarUrl);
            this.setAvatarImage(avatarUrl);
            this.hasCustomAvatar = true;
        } else {
            this.resetAvatarToDefault();
        }
        
        // Обновляем инициалы аватара
        this.updateAvatar();
        
        // Блокируем поля после обновления
        this.setFieldsReadOnly(true);
        
        console.log('✅ Profile data applied to form');
    }

    async refreshUserData() {
        console.log('🔄 Refreshing user data...');
        
        try {
            if (window.apiService.isAuthenticated()) {
                // Загружаем свежие данные с сервера
                const userData = await window.apiService.getCurrentUser();
                console.log('✅ Fresh user data from server:', userData);
                
                // Обновляем интерфейс
                this.setProfileData(userData);
                
                // Сохраняем в localStorage
                this.saveUserToLocalStorage(userData);
            } else {
                // Перезагружаем из localStorage
                this.loadLocalUserData();
            }
        } catch (error) {
            console.error('❌ Error refreshing user data:', error);
        }
    }

    // Удаление аккаунта
    async deleteAccount() {
        // Подтверждение удаления
        const confirmMessage = 'Вы действительно хотите удалить аккаунт? Это действие нельзя отменить.';
        if (!confirm(confirmMessage)) {
            return;
        }

        // Дополнительное подтверждение
        const doubleConfirm = prompt('Для подтверждения введите "УДАЛИТЬ":');
        if (doubleConfirm !== 'УДАЛИТЬ') {
            this.showErrorMessage('Удаление аккаунта отменено');
            return;
        }

        try {
            this.showLoading('Удаление аккаунта...');
            
            // Если пользователь авторизован, отправляем запрос на сервер
            if (window.apiService && window.apiService.isAuthenticated()) {
                await window.apiService.deleteAccount();
            }
            
            // Очищаем локальные данные
            localStorage.removeItem('auth_token');
            localStorage.removeItem('fashioneco_current_user');
            
            // Очищаем состояние авторизации
            if (window.authState) {
                window.authState.currentUser = null;
                window.authState.updateUI();
            }
            
            this.hideLoading();
            this.showSuccessMessage('Аккаунт успешно удален');
            
            // Перенаправляем на главную страницу через 2 секунды
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
            
        } catch (error) {
            this.hideLoading();
            console.error('❌ Error deleting account:', error);
            this.showErrorMessage('Ошибка при удалении аккаунта: ' + (error.message || 'Неизвестная ошибка'));
        }
    }
}

// Инициализация без проверки авторизации
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔧 DOM Content Loaded - Profile initializing');
    
    try {
        const userProfile = new UserProfile();
        window.userProfile = userProfile;
        console.log('✅ UserProfile initialized successfully');
    } catch (error) {
        console.error('❌ Error initializing UserProfile:', error);
        
        // Показываем ошибку на странице
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #f8d7da;
            color: #721c24;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #f5c6cb;
            text-align: center;
            z-index: 10000;
        `;
        errorDiv.innerHTML = `
            <h3>Ошибка загрузки профиля</h3>
            <p>${error.message}</p>
            <button onclick="location.reload()" style="margin-top: 10px; padding: 8px 16px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">
                Перезагрузить
            </button>
        `;
        document.body.appendChild(errorDiv);
    }
});

console.log('🔧 profile.js loaded');