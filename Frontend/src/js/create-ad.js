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

        const mainCategoryInput = document.getElementById('ad-main-category');
        if (mainCategoryInput && ad.main_category) {
            mainCategoryInput.value = ad.main_category;
            console.log(`✅ Установлена категория: ${ad.main_category} для элемента`, mainCategoryInput);
        }
        
        const subCategoryInput = document.getElementById('ad-sub-category');
        if (subCategoryInput && ad.sub_category) {
            subCategoryInput.value = ad.sub_category;
        }
        
        const seasonInput = document.getElementById('ad-season');
        if (seasonInput && ad.season) {
            seasonInput.value = ad.season;
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

    handleImageUpload(files) {
        if (!files || files.length === 0) return;

        console.log(`📤 Выбрано ${files.length} изображений...`);

        for (let file of Array.from(files)) {
            try {
                // Создаем временное превью
                const previewUrl = URL.createObjectURL(file);
                
                // Сохраняем файл для последующей загрузки
                const imageData = {
                    file: file, // Сохраняем сам файл
                    preview_url: previewUrl,
                    filename: file.name,
                    size: file.size,
                    type: file.type
                };
                
                // Проверяем, не загружено ли уже это изображение
                const isDuplicate = this.uploadedImages.some(img => 
                    img.filename === file.name && img.size === file.size
                );
                if (isDuplicate) {
                    console.warn('⚠️ Изображение уже добавлено, пропускаем:', file.name);
                    URL.revokeObjectURL(previewUrl);
                    continue;
                }
                
                this.uploadedImages.push(imageData);
                this.addImagePreview(imageData);
                
            } catch (error) {
                console.error('❌ Ошибка обработки изображения:', error);
                alert(`Ошибка обработки изображения ${file.name}: ${error.message}`);
            }
        }

        // Очищаем input
        if (this.elements.imageInput) {
            this.elements.imageInput.value = '';
        }
    }

    async uploadImagesToAd(adId) {
        if (!adId || this.uploadedImages.length === 0) return;
        
        console.log(`📤 Загрузка ${this.uploadedImages.length} изображений к объявлению ${adId}`);
        
        for (const imageData of this.uploadedImages) {
            try {
                const formData = new FormData();
                formData.append('files', imageData.file); // Важно: 'files' во множественном числе
                
                // Используем эндпоинт для загрузки изображений к объявлению
                const response = await fetch(`http://localhost:8000/api/ads/${adId}/images`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${window.apiService.token}`,
                    },
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                
                const result = await response.json();
                console.log('✅ Изображение загружено:', result);
                
            } catch (error) {
                console.error('❌ Ошибка загрузки изображения:', error);
                // Продолжаем загрузку остальных изображений
            }
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

        // Собираем данные формы - ПРАВИЛЬНАЯ СТРУКТУРА
        const formData = {
            type: this.elements.adType?.value,
            title: document.getElementById('ad-title')?.value,
            description: document.getElementById('ad-description')?.value || "",
            price: this.elements.adPrice?.value ? parseFloat(this.elements.adPrice.value) : null,
            condition: document.getElementById('ad-condition')?.value,
            
            // ПРАВИЛЬНЫЕ поля категорий (должны соответствовать HTML)
            main_category: document.getElementById('ad-main-category')?.value || null,
            sub_category: document.getElementById('ad-sub-category')?.value || null,
            season: document.getElementById('ad-season')?.value || null,
            
            size: document.getElementById('ad-size')?.value || null,
            brand: document.getElementById('ad-brand')?.value || null,
            
            // Дополнительные поля (убедитесь, что есть в HTML)
            colors: this.getSelectedColors(), // функция возвращает null, если ничего не выбрано
            tags: document.getElementById('ad-tags')?.value || null,
        };

        console.log('📤 Собираемые данные формы:', formData);

        // Валидация
        if (!formData.type) {
            alert('Выберите тип объявления');
            return;
        }

        if (!formData.title || formData.title.trim().length === 0) {
            alert('Введите название объявления');
            return;
        }

        if (formData.title.length > 200) {
            alert('Название не должно превышать 200 символов');
            return;
        }

        if (formData.type === 'sell' && formData.price === null) {
            alert('Для объявлений о продаже необходимо указать цену');
            return;
        }

        if (formData.type === 'sell' && formData.price !== null && formData.price < 0) {
            alert('Цена не может быть отрицательной');
            return;
        }

        if (!formData.condition) {
            alert('Выберите состояние товара');
            return;
        }

        // Проверка main_category
        if (!formData.main_category) {
            if (confirm('Не выбрана основная категория. Продолжить без категории?')) {
                // Можно продолжить без категории
            } else {
                return;
            }
        }

        // Добавляем изображения - берем только пути к файлам, убираем дубликаты
        formData.images = [...new Set(this.uploadedImages.map(img => img.file_path))];
        
        try {
            if (this.elements.submitBtn) {
                this.elements.submitBtn.disabled = true;
                this.elements.submitBtn.textContent = this.editMode ? 'Сохранение...' : 'Создание...';
            }

            let result;
            let adId;

            if (this.editMode) {
                // Редактирование объявления
                console.log('✏️ Обновление объявления:', this.editId, formData);
                result = await window.apiService.updateAd(this.editId, formData);
                adId = this.editId;
                alert('Объявление успешно обновлено!', adId);
            } else {
                // Создание нового объявления
                console.log('➕ Создание объявления:', formData);
                result = await window.apiService.createAd(formData);
                adId = result.id;
                alert('Объявление успешно создано!', adId);
            }

            // ТЕПЕРЬ загружаем изображения к объявлению
            if (this.uploadedImages.length > 0) {
                console.log(`📤 Прикрепление ${this.uploadedImages.length} изображений к объявлению ${adId}`);
                await this.attachImagesToAd(adId);
            }

            alert(this.editMode ? 'Объявление успешно обновлено!' : 'Объявление успешно создано!');

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

    async attachImagesToAd(adId, images) {
    //     if (!adId || this.uploadedImages.length === 0) return;
    
    //     const apiService = window.apiService;
        
    //     // Создаем FormData для загрузки изображений
    //     for (const image of this.uploadedImages) {
    //         try {
    //             // Нужно загрузить файлы заново, так как мы не сохранили файлы
    //             // Вместо этого можно сохранить файлы при загрузке и переиспользовать
                
    //             console.log('⚠️ Изображения загружены отдельно от объявления. Нужно исправить логику загрузки.');
                
    //             // Временное решение: показываем предупреждение
    //             console.warn('Для корректной работы нужно изменить логику загрузки изображений');
                
    //         } catch (error) {
    //             console.error('❌ Ошибка прикрепления изображения:', error);
    //         }
    //     }
    // }
        if (!adId || !images || images.length === 0) return;
        
        const apiService = window.apiService;
        
        for (const image of images) {
            try {
                // Здесь нужно перезагрузить файлы или использовать уже загруженные пути
                // В зависимости от того, как работает ваш бэкенд
                
                // Вариант 1: Если изображения уже загружены ранее
                const response = await apiService.request(`/ads/${adId}/images`, {
                    method: 'POST',
                    body: JSON.stringify({
                        file_path: image.file_path,
                        filename: image.server_filename || image.filename
                    }),
                    headers: {
                        'Content-Type': 'application/json',
                        ...apiService.getAuthHeaders()
                    }
                });
                
                console.log('✅ Изображение прикреплено:', response);
                
            } catch (error) {
                console.error('❌ Ошибка прикрепления изображения:', error);
                // Можно продолжить, даже если одно изображение не загрузилось
            }
        }
    }

    // Вспомогательная функция для получения выбранных цветов
    getSelectedColors() {
        const colors = [];
        // Если у вас есть чекбоксы или мультиселект для цветов
        const colorCheckboxes = document.querySelectorAll('input[name="colors"]:checked');
        colorCheckboxes.forEach(checkbox => {
            colors.push(checkbox.value);
        });
        return colors.length > 0 ? colors : null;
    }
} // Закрывающая скобка класса CreateAdPage

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