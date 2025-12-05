class CreateAdPage {
    constructor() {
        this.uploadedImages = []; // Массив объектов {file_path, preview_url, filename}
        this.elements = {
            form: document.getElementById('create-ad-form'),
            adType: document.getElementById('ad-type'),
            priceField: document.getElementById('price-field'),
            adPrice: document.getElementById('ad-price'),
            imageInput: document.getElementById('image-input'),
            imageUploadArea: document.getElementById('image-upload-area'),
            imagePreviewContainer: document.getElementById('image-preview-container'),
            submitBtn: document.getElementById('submit-btn')
        };
        
        this.init();
    }

    init() {
        console.log('🔄 Инициализация страницы создания объявления');
        
        // Проверяем авторизацию
        if (!window.apiService || !window.apiService.isAuthenticated()) {
            alert('Для создания объявления необходимо войти в систему.');
            window.location.href = 'login.html';
            return;
        }
        
        // Проверяем, режим редактирования или создания
        const urlParams = new URLSearchParams(window.location.search);
        const editId = urlParams.get('edit');
        
        if (editId) {
            this.editMode = true;
            this.editId = parseInt(editId);
            this.loadAdForEdit();
            // Изменяем текст кнопки
            if (this.elements.submitBtn) {
                this.elements.submitBtn.textContent = 'СОХРАНИТЬ ИЗМЕНЕНИЯ';
            }
        } else {
            this.editMode = false;
        }
        
        this.attachEventListeners();
    }

    async loadAdForEdit() {
        try {
            console.log('📝 Загрузка объявления для редактирования:', this.editId);
            const ad = await window.apiService.getAd(this.editId);
            
            // Заполняем форму данными объявления
            this.populateForm(ad);
            
            // Изменяем заголовок страницы
            const titleElement = document.querySelector('h1');
            if (titleElement) {
                titleElement.textContent = 'РЕДАКТИРОВАНИЕ ОБЪЯВЛЕНИЯ';
            }
            
        } catch (error) {
            console.error('❌ Ошибка загрузки объявления:', error);
            alert('Не удалось загрузить объявление для редактирования');
            window.location.href = 'my-ads.html';
        }
    }

    populateForm(ad) {
        // Заполняем все поля формы
        if (this.elements.adType && ad.type) {
            this.elements.adType.value = ad.type;
            this.handleAdTypeChange(ad.type);
        }
        
        const titleInput = document.getElementById('ad-title');
        if (titleInput && ad.title) {
            titleInput.value = ad.title;
        }
        
        const descriptionInput = document.getElementById('ad-description');
        if (descriptionInput && ad.description) {
            descriptionInput.value = ad.description || '';
        }
        
        if (this.elements.adPrice && ad.price) {
            this.elements.adPrice.value = ad.price;
        }
        
        const conditionInput = document.getElementById('ad-condition');
        if (conditionInput && ad.condition) {
            conditionInput.value = ad.condition;
        }
        
        const sizeInput = document.getElementById('ad-size');
        if (sizeInput && ad.size) {
            sizeInput.value = ad.size;
        }
        
        const brandInput = document.getElementById('ad-brand');
        if (brandInput && ad.brand) {
            brandInput.value = ad.brand;
        }
        
        // Загружаем изображения
        if (ad.images && ad.images.length > 0) {
            this.uploadedImages = ad.images.map(img => ({
                file_path: img,
                preview_url: this.getImageUrl(img),
                filename: img.split('/').pop()
            }));
            this.renderImagePreviews();
        }
    }

    getImageUrl(imagePath) {
        if (!imagePath) return '';
        if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
            return imagePath;
        }
        const baseUrl = 'http://localhost:8000/static/';
        let cleanPath = imagePath.startsWith('/') ? imagePath.slice(1) : imagePath;
        if (cleanPath.startsWith('file_storage/')) {
            cleanPath = cleanPath.replace('file_storage/', '');
        }
        return `${baseUrl}${cleanPath}`;
    }

    attachEventListeners() {
        // Обработчик изменения типа объявления
        if (this.elements.adType) {
            this.elements.adType.addEventListener('change', (e) => {
                this.handleAdTypeChange(e.target.value);
            });
        }

        // Обработчик загрузки изображений
        if (this.elements.imageInput) {
            this.elements.imageInput.addEventListener('change', (e) => {
                this.handleImageUpload(e.target.files);
            });
        }

        // Обработчик клика на область загрузки
        if (this.elements.imageUploadArea) {
            this.elements.imageUploadArea.addEventListener('click', () => {
                if (this.elements.imageInput) {
                    this.elements.imageInput.click();
                }
            });
        }

        // Обработчик отправки формы
        if (this.elements.form) {
            this.elements.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmit();
            });
        }
    }

    handleAdTypeChange(type) {
        // Если тип "sell", показываем поле цены и делаем его обязательным
        if (type === 'sell') {
            if (this.elements.priceField) {
                this.elements.priceField.style.display = 'block';
            }
            if (this.elements.adPrice) {
                this.elements.adPrice.required = true;
            }
        } else {
            if (this.elements.priceField) {
                this.elements.priceField.style.display = 'none';
            }
            if (this.elements.adPrice) {
                this.elements.adPrice.required = false;
                this.elements.adPrice.value = '';
            }
        }
    }

    async handleImageUpload(files) {
        if (!files || files.length === 0) return;

        console.log(`📤 Загрузка ${files.length} изображений...`);

        for (let file of Array.from(files)) {
            try {
                // Создаем временное превью для отображения во время загрузки
                const previewUrl = URL.createObjectURL(file);
                
                // Загружаем на сервер
                const response = await window.apiService.uploadAdImage(file);
                console.log('✅ Изображение загружено:', response);
                
                // Проверяем, не загружено ли уже это изображение
                const isDuplicate = this.uploadedImages.some(img => img.file_path === response.file_path);
                if (isDuplicate) {
                    console.warn('⚠️ Изображение уже загружено, пропускаем:', response.file_path);
                    URL.revokeObjectURL(previewUrl);
                    continue;
                }
                
                // Сохраняем информацию об изображении
                const imageData = {
                    file_path: response.file_path,
                    preview_url: previewUrl,
                    filename: file.name,
                    server_filename: response.filename
                };
                
                this.uploadedImages.push(imageData);
                
                // Добавляем превью с правильной связью
                this.addImagePreview(imageData);
            } catch (error) {
                console.error('❌ Ошибка загрузки изображения:', error);
                alert(`Ошибка загрузки изображения ${file.name}: ${error.message}`);
            }
        }

        // Очищаем input, чтобы можно было загрузить те же файлы снова
        if (this.elements.imageInput) {
            this.elements.imageInput.value = '';
        }
    }

    addImagePreview(imageData) {
        const preview = document.createElement('div');
        preview.className = 'image-preview';
        preview.setAttribute('data-file-path', imageData.file_path);
        preview.innerHTML = `
            <img src="${imageData.preview_url}" alt="${imageData.filename}">
            <button type="button" class="remove-image-btn" data-file-path="${imageData.file_path}">×</button>
        `;

        // Обработчик удаления изображения
        const removeBtn = preview.querySelector('.remove-image-btn');
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.removeImagePreview(preview, imageData.file_path);
        });

        if (this.elements.imagePreviewContainer) {
            this.elements.imagePreviewContainer.appendChild(preview);
        }
    }

    removeImagePreview(preview, filePath) {
        // Освобождаем URL превью
        const imageData = this.uploadedImages.find(img => img.file_path === filePath);
        if (imageData && imageData.preview_url) {
            URL.revokeObjectURL(imageData.preview_url);
        }
        
        // Удаляем из массива загруженных изображений
        this.uploadedImages = this.uploadedImages.filter(img => img.file_path !== filePath);
        
        // Удаляем превью из DOM
        preview.remove();
    }

    async handleFormSubmit() {
        if (!this.elements.form) return;

        // Собираем данные формы
        const formData = {
            type: this.elements.adType?.value,
            title: document.getElementById('ad-title')?.value,
            description: document.getElementById('ad-description')?.value || null,
            price: this.elements.adPrice?.value ? parseFloat(this.elements.adPrice.value) : null,
            condition: document.getElementById('ad-condition')?.value,
            category: document.getElementById('ad-category')?.value,
            size: document.getElementById('ad-size')?.value || null,
            brand: document.getElementById('ad-brand')?.value || null,
        };

        // Валидация
        if (!formData.type) {
            alert('Выберите тип объявления');
            return;
        }

        if (!formData.title) {
            alert('Введите название объявления');
            return;
        }

        if (formData.type === 'sell' && !formData.price) {
            alert('Для объявлений о продаже необходимо указать цену');
            return;
        }

        if (!formData.condition) {
            alert('Выберите состояние товара');
            return;
        }

        if (!formData.category) {
            alert('Выберите категорию');
            return;
        }

        // Добавляем изображения - берем только пути к файлам, убираем дубликаты
        formData.images = [...new Set(this.uploadedImages.map(img => img.file_path))];
        
        try {
            if (this.elements.submitBtn) {
                this.elements.submitBtn.disabled = true;
                this.elements.submitBtn.textContent = this.editMode ? 'Сохранение...' : 'Создание...';
            }

            let result;
            if (this.editMode) {
                // Редактирование объявления
                console.log('✏️ Обновление объявления:', this.editId, formData);
                result = await window.apiService.updateAd(this.editId, formData);
                alert('Объявление успешно обновлено!');
            } else {
                // Создание нового объявления
                console.log('➕ Создание объявления:', formData);
                result = await window.apiService.createAd(formData);
                alert('Объявление успешно создано!');
            }

            // Перенаправляем на страницу моих объявлений
            window.location.href = 'my-ads.html';
        } catch (error) {
            console.error('❌ Ошибка:', error);
            alert(`Ошибка: ${error.message || 'Не удалось сохранить объявление'}`);
        } finally {
            if (this.elements.submitBtn) {
                this.elements.submitBtn.disabled = false;
                this.elements.submitBtn.textContent = this.editMode ? 'СОХРАНИТЬ ИЗМЕНЕНИЯ' : 'СОЗДАТЬ ОБЪЯВЛЕНИЕ';
            }
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    if (window.apiService) {
        window.createAdPage = new CreateAdPage();
    } else {
        window.addEventListener('load', () => {
            window.createAdPage = new CreateAdPage();
        });
    }
});

