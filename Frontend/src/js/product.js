class ProductPage {
    constructor() {
        this.adId = null;
        this.adData = null;
        this.sellerData = null;
        
        this.currentImageIndex = 0;
        this.images = [];
        
        this.elements = {
            mainImage: document.getElementById('main-image'),
            mainImageContainer: document.querySelector('.main-image-container'),
            secondaryImageContainer: document.getElementById('secondary-image-container'),
            prevBtn: document.getElementById('prev-image-btn'),
            nextBtn: document.getElementById('next-image-btn'),
            imageIndicator: document.getElementById('image-indicator'),
            productTitle: document.getElementById('product-title'),
            productPrice: document.getElementById('product-price'),
            productDescription: document.getElementById('product-description'),
            conditionList: document.getElementById('condition-list'),
            sellerInfo: document.getElementById('seller-info'),
            btnContact: document.getElementById('btn-contact'),
            btnCart: document.getElementById('btn-cart'),
            contactModal: document.getElementById('contact-modal'),
            modalClose: document.getElementById('modal-close'),
            contactInfo: document.getElementById('contact-info'),
            sellerName: document.getElementById('seller-name'),
            sellerPhone: document.getElementById('seller-phone'),
            sellerEmail: document.getElementById('seller-email')
        };

        this.init();
    }

    init() {
        // Получаем ID товара из URL
        const urlParams = new URLSearchParams(window.location.search);
        this.adId = urlParams.get('id');
        
        if (!this.adId) {
            this.showError('ID товара не указан');
            return;
        }

        // Загружаем данные товара
        this.loadProductData();

        // Привязываем события
        if (this.elements.btnContact) {
            this.elements.btnContact.addEventListener('click', () => this.showContacts());
        }
        
        if (this.elements.btnCart) {
            this.elements.btnCart.addEventListener('click', () => this.addToCart());
        }

        if (this.elements.modalClose) {
            this.elements.modalClose.addEventListener('click', () => this.hideContacts());
        }

        // Закрытие модального окна при клике вне его
        if (this.elements.contactModal) {
            this.elements.contactModal.addEventListener('click', (e) => {
                if (e.target === this.elements.contactModal) {
                    this.hideContacts();
                }
            });
        }

        // Навигация по изображениям
        if (this.elements.prevBtn) {
            this.elements.prevBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.showPreviousImage();
            });
        }

        if (this.elements.nextBtn) {
            this.elements.nextBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.showNextImage();
            });
        }

        // Навигация клавиатурой
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                this.showPreviousImage();
            } else if (e.key === 'ArrowRight') {
                this.showNextImage();
            }
        });

        // Переключение по клику на главное изображение
        if (this.elements.mainImageContainer) {
            this.elements.mainImageContainer.addEventListener('click', (e) => {
                // Если клик не по кнопке навигации, переключаем изображение
                if (!e.target.closest('.image-nav-btn')) {
                    this.showNextImage();
                }
            });
        }
    }

    async loadProductData() {
        try {
            console.log('🔄 Загрузка данных товара:', this.adId);
            
            // Загружаем данные объявления
            this.adData = await window.apiService.getAd(this.adId);
            console.log('✅ Данные товара загружены:', this.adData);

            // Отображаем данные
            this.displayProductData();

            // Загружаем данные продавца (если нужно)
            // Пока оставим это на будущее, так как нужен эндпоинт для получения пользователя по ID
            
        } catch (error) {
            console.error('❌ Ошибка загрузки товара:', error);
            this.showError('Не удалось загрузить данные товара: ' + error.message);
        }
    }

    displayProductData() {
        if (!this.adData) return;

        // Заголовок
        if (this.elements.productTitle) {
            this.elements.productTitle.textContent = this.adData.title || 'Без названия';
        }

        // Цена
        if (this.elements.productPrice) {
            if (this.adData.price && this.adData.price > 0) {
                this.elements.productPrice.textContent = `${Math.round(this.adData.price)} ₽`;
            } else {
                this.elements.productPrice.textContent = 'Обмен';
            }
        }

        // Описание
        if (this.elements.productDescription) {
            this.elements.productDescription.textContent = this.adData.description || 'Описание отсутствует';
        }

        // Изображения
        this.displayImages();

        // Состояние
        this.displayCondition();

        // Информация о продавце
        if (this.elements.sellerInfo) {
            // Пока просто показываем стандартное сообщение
            // В будущем можно будет проверить, разрешил ли продавец показывать контакты
            this.elements.sellerInfo.textContent = 'ПРОДАВЕЦ ВЫБРАЛ ОСТАВИТЬ НОМЕР ТЕЛЕФОНА ДЛЯ СВЯЗИ';
        }
    }

    displayImages() {
        const images = this.adData.images || [];
        const baseUrl = 'http://localhost:8000/static/';

        // Сохраняем список изображений для навигации
        if (images.length > 0) {
            this.images = images.map(img => this.normalizeImageUrl(img, baseUrl));
        } else {
            this.images = [this.getPlaceholderImage()];
        }

        // Устанавливаем начальное изображение
        this.currentImageIndex = 0;
        this.updateMainImage();

        // Создаем миниатюры
        this.createThumbnails();
    }

    updateMainImage() {
        if (this.elements.mainImage && this.images.length > 0) {
            const imageUrl = this.images[this.currentImageIndex];
            this.elements.mainImage.src = imageUrl;
            this.elements.mainImage.alt = this.adData.title || 'Товар';
            this.elements.mainImage.onerror = () => {
                this.elements.mainImage.src = this.getPlaceholderImage();
            };
        } else if (this.elements.mainImage) {
            this.elements.mainImage.src = this.getPlaceholderImage();
        }

        // Показываем/скрываем кнопки навигации
        this.updateNavigationButtons();

        // Обновляем индикатор
        this.updateImageIndicator();

        // Обновляем активную миниатюру
        this.updateActiveThumbnail();
    }

    updateNavigationButtons() {
        // Показываем кнопки только если изображений больше одного
        const showButtons = this.images.length > 1;
        if (this.elements.prevBtn) {
            if (showButtons) {
                this.elements.prevBtn.style.display = 'flex';
            } else {
                this.elements.prevBtn.style.display = 'none';
            }
        }
        if (this.elements.nextBtn) {
            if (showButtons) {
                this.elements.nextBtn.style.display = 'flex';
            } else {
                this.elements.nextBtn.style.display = 'none';
            }
        }
    }

    createThumbnails() {
        if (!this.elements.secondaryImageContainer) return;

        // Очищаем контейнер
        this.elements.secondaryImageContainer.innerHTML = '';

        // Создаем миниатюры для всех изображений
        this.images.forEach((imageUrl, index) => {
            const thumbnailItem = document.createElement('div');
            thumbnailItem.className = `secondary-image-item ${index === 0 ? 'active' : ''}`;
            thumbnailItem.setAttribute('data-index', index);
            
            const thumbnailImg = document.createElement('img');
            thumbnailImg.src = imageUrl;
            thumbnailImg.alt = `${this.adData.title || 'Товар'} - фото ${index + 1}`;
            thumbnailImg.className = 'secondary-image';
            thumbnailImg.onerror = () => {
                thumbnailImg.src = this.getPlaceholderImage();
            };

            thumbnailItem.appendChild(thumbnailImg);
            
            // Обработчик клика на миниатюру
            thumbnailItem.addEventListener('click', () => {
                this.currentImageIndex = index;
                this.updateMainImage();
            });

            this.elements.secondaryImageContainer.appendChild(thumbnailItem);
        });

        // Если изображений нет, скрываем контейнер миниатюр
        if (this.images.length === 0) {
            this.elements.secondaryImageContainer.style.display = 'none';
        }
    }

    updateActiveThumbnail() {
        if (!this.elements.secondaryImageContainer) return;

        const thumbnails = this.elements.secondaryImageContainer.querySelectorAll('.secondary-image-item');
        thumbnails.forEach((thumbnail, index) => {
            if (index === this.currentImageIndex) {
                thumbnail.classList.add('active');
            } else {
                thumbnail.classList.remove('active');
            }
        });
    }

    updateImageIndicator() {
        if (!this.elements.imageIndicator || this.images.length <= 1) {
            if (this.elements.imageIndicator) {
                this.elements.imageIndicator.innerHTML = '';
            }
            return;
        }

        // Очищаем индикатор
        this.elements.imageIndicator.innerHTML = '';

        // Создаем точки для каждого изображения
        this.images.forEach((_, index) => {
            const dot = document.createElement('div');
            dot.className = `image-indicator-dot ${index === this.currentImageIndex ? 'active' : ''}`;
            dot.setAttribute('data-index', index);
            
            dot.addEventListener('click', () => {
                this.currentImageIndex = index;
                this.updateMainImage();
            });

            this.elements.imageIndicator.appendChild(dot);
        });
    }

    showNextImage() {
        if (this.images.length === 0) return;
        this.currentImageIndex = (this.currentImageIndex + 1) % this.images.length;
        this.updateMainImage();
    }

    showPreviousImage() {
        if (this.images.length === 0) return;
        this.currentImageIndex = (this.currentImageIndex - 1 + this.images.length) % this.images.length;
        this.updateMainImage();
    }

    normalizeImageUrl(imagePath, baseUrl) {
        if (!imagePath) return this.getPlaceholderImage();
        
        // БЛОКИРУЕМ все ссылки на via.placeholder.com - заменяем на локальную заглушку
        if (imagePath.includes('via.placeholder.com') || imagePath.includes('placeholder.com')) {
            console.warn('⚠️ Заблокирована попытка загрузить изображение с via.placeholder.com, используется локальная заглушка');
            return this.getPlaceholderImage();
        }
        
        // Если путь уже полный URL (но не placeholder), возвращаем как есть
        if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
            return imagePath;
        }
        
        // Убираем начальный слэш
        let cleanPath = imagePath.startsWith('/') ? imagePath.slice(1) : imagePath;
        
        // Если путь содержит "media/ads/", оставляем как есть
        // Если путь содержит "file_storage/", убираем этот префикс
        if (cleanPath.startsWith('file_storage/')) {
            cleanPath = cleanPath.replace('file_storage/', '');
        }
        
        return `${baseUrl}${cleanPath}`;
    }

    displayCondition() {
        if (!this.elements.conditionList) return;

        const condition = this.adData.condition || '';
        const conditionText = this.getConditionText(condition);
        
        // Очищаем список
        this.elements.conditionList.innerHTML = '';

        // Формируем пункты состояния
        const conditionPoints = [
            `СОСТОЯНИЕ: ${conditionText.toUpperCase()}`,

            this.adData.main_category ? `КАТЕГОРИЯ: ${this.getCategoryText(this.adData.main_category).toUpperCase()}.` : null,
            this.adData.sub_category ? `ПОДКАТЕГОРИЯ: ${this.getSubCategoryText(this.adData.sub_category).toUpperCase()}.` : null,
            this.adData.season ? `СЕЗОН: ${this.getSeasonText(this.adData.season).toUpperCase()}.` : null,

            this.adData.brand ? `БРЕНД: ${this.adData.brand.toUpperCase()}` : null,
            this.adData.size ? `РАЗМЕР: ${this.adData.size.toUpperCase()}` : null,
        ].filter(Boolean);

        // Если нет информации о состоянии, используем базовую информацию
        if (conditionPoints.length === 0) {
            conditionPoints.push('Информация о состоянии отсутствует.');
        }

        // Создаем элементы списка
        conditionPoints.forEach(point => {
            const li = document.createElement('li');
            li.textContent = point;
            this.elements.conditionList.appendChild(li);
        });
    }

    getConditionText(condition) {
        if (!condition) return 'НЕ УКАЗАНО';
        
        const conditionLower = condition.toLowerCase();
        
        const conditionMap = {
            'new': 'НОВОЕ', 
            'excellent': 'ОТЛИЧНОЕ',
            'good': 'ХОРОШЕЕ',
            'satisfactory': 'УДОВЛЕТВОРИТЕЛЬНОЕ',
            'needs_repair': 'ТРЕБУЕТ РЕМОНТА'
        };
        
        return conditionMap[conditionLower] || condition.toUpperCase();
    }

    getCategoryText(category) {
        const categoryMap = {
            'men': 'Мужская одежда',
            'women': 'Женская одежда',
            'kids': 'Детская одежда',
            'unisex': 'Унисекс',
            'baby': 'Детская (0-3 лет)'
        };
        return categoryMap[category] || category;
    }

    getSubCategoryText(subcategory) {
        const subcategoryMap = {
            'formal': 'Деловая/формальная',
            'casual': 'Повседневная',
            'sports': 'Спортивная',
            'outerwear': 'Верхняя одежда',
            'underwear': 'Нижнее белье',
            'swimwear': 'Пляжная одежда',
            'accessories': 'Аксессуары',
            'shoes': 'Обувь',
            'bags': 'Сумки',
            'jewelry': 'Украшения'
        };
        return subcategoryMap[subcategory] || subcategory;
    }

    getSeasonText(season) {
        const seasonMap = {
            'winter': 'Зима',
            'spring': 'Весна',
            'summer': 'Лето',
            'autumn': 'Осень',
            'all_season': 'Всесезонная'
        };
        return seasonMap[season] || season;
    }

    async showContacts() {
        if (!this.elements.contactModal || !this.adData) return;

        try {
            // Показываем модальное окно с загрузкой
            this.elements.contactModal.classList.add('show');
            
            // Устанавливаем заглушки пока загружаются данные
            if (this.elements.sellerName) {
                this.elements.sellerName.textContent = 'Загрузка...';
            }
            if (this.elements.sellerPhone) {
                this.elements.sellerPhone.textContent = 'Загрузка...';
            }
            if (this.elements.sellerEmail) {
                this.elements.sellerEmail.textContent = 'Загрузка...';
            }

            // Загружаем данные продавца
            console.log('📞 Загрузка контактов продавца, user_id:', this.adData.user_id);
            const sellerInfo = await window.apiService.getUserPublicInfo(this.adData.user_id);
            console.log('✅ Контакты продавца загружены:', sellerInfo);

            // Отображаем данные продавца
            if (this.elements.sellerName) {
                this.elements.sellerName.textContent = sellerInfo.name 
                    ? `Имя: ${sellerInfo.name}` 
                    : 'Имя: Не указано';
            }
            if (this.elements.sellerPhone) {
                this.elements.sellerPhone.textContent = sellerInfo.phone 
                    ? `Телефон: ${sellerInfo.phone}` 
                    : 'Телефон: Не указан';
            }
            if (this.elements.sellerEmail) {
                this.elements.sellerEmail.textContent = sellerInfo.email 
                    ? `Email: ${sellerInfo.email}` 
                    : 'Email: Не указан';
            }
        } catch (error) {
            console.error('❌ Ошибка загрузки контактов:', error);
            
            // Показываем ошибку в модальном окне
            if (this.elements.sellerName) {
                this.elements.sellerName.textContent = 'Ошибка загрузки';
            }
            if (this.elements.sellerPhone) {
                this.elements.sellerPhone.textContent = 'Не удалось загрузить контакты';
            }
            if (this.elements.sellerEmail) {
                this.elements.sellerEmail.textContent = '';
            }
        }
    }

    hideContacts() {
        if (this.elements.contactModal) {
            this.elements.contactModal.classList.remove('show');
        }
    }

    addToCart() {
        // TODO: Реализовать добавление в корзину
        console.log('🛒 Добавление в корзину:', this.adId);
        alert('Товар добавлен в корзину!');
    }

    getPlaceholderImage() {
        // SVG заглушка вместо внешнего сервиса
        const svg = `
            <svg width="500" height="500" xmlns="http://www.w3.org/2000/svg">
                <rect width="500" height="500" fill="#F3E4D3"/>
                <text x="50%" y="45%" text-anchor="middle" font-family="Arial, sans-serif" font-size="32" fill="#4B0505">Нет изображения</text>
                <text x="50%" y="55%" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" fill="#6b7280">FASHIONECHO</text>
            </svg>
        `.trim().replace(/\s+/g, ' ');
        return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
    }

    showError(message) {
        console.error('❌ Ошибка:', message);
        if (this.elements.productTitle) {
            this.elements.productTitle.textContent = 'Ошибка загрузки';
        }
        if (this.elements.productDescription) {
            this.elements.productDescription.textContent = message;
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.productPage = new ProductPage();
});

