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
        
        this.attachEventListeners();
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
        const imagePaths = this.uploadedImages.map(img => img.file_path).filter(path => path); // Фильтруем пустые пути
        formData.images = [...new Set(imagePaths)]; // Убираем дубликаты
        console.log('📸 Отправляемые изображения:', formData.images);

        try {
            // Блокируем кнопку отправки
            if (this.elements.submitBtn) {
                this.elements.submitBtn.disabled = true;
                this.elements.submitBtn.textContent = 'Создание...';
            }

            console.log('📤 Отправка объявления:', formData);
            const createdAd = await window.apiService.createAd(formData);
            
            console.log('✅ Объявление создано:', createdAd);
            alert('Объявление успешно создано!');
            
            // Перенаправляем на страницу "Мои объявления"
            window.location.href = 'my-ads.html';
            
        } catch (error) {
            console.error('❌ Ошибка создания объявления:', error);
            alert(`Ошибка создания объявления: ${error.message || 'Неизвестная ошибка'}`);
        } finally {
            // Разблокируем кнопку
            if (this.elements.submitBtn) {
                this.elements.submitBtn.disabled = false;
                this.elements.submitBtn.textContent = 'СОЗДАТЬ ОБЪЯВЛЕНИЕ';
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

