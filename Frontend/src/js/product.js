class ProductPage {
    constructor() {
        this.adId = null;
        this.adData = null;
        this.sellerData = null;
        
        this.elements = {
            mainImage: document.getElementById('main-image'),
            secondaryImage: document.getElementById('secondary-image'),
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

        // Главное изображение
        if (this.elements.mainImage && images.length > 0) {
            const imageUrl = this.normalizeImageUrl(images[0], baseUrl);
            this.elements.mainImage.src = imageUrl;
            this.elements.mainImage.alt = this.adData.title || 'Товар';
            this.elements.mainImage.onerror = () => {
                this.elements.mainImage.src = this.getPlaceholderImage();
            };
        } else if (this.elements.mainImage) {
            this.elements.mainImage.src = this.getPlaceholderImage();
        }

        // Второе изображение
        if (this.elements.secondaryImage) {
            if (images.length > 1) {
                const imageUrl = this.normalizeImageUrl(images[1], baseUrl);
                this.elements.secondaryImage.src = imageUrl;
                this.elements.secondaryImage.alt = this.adData.title || 'Товар';
                this.elements.secondaryImage.onerror = () => {
                    this.elements.secondaryImage.style.display = 'none';
                };
            } else if (images.length === 1) {
                // Если только одно изображение, используем его и для второго места
                const imageUrl = this.normalizeImageUrl(images[0], baseUrl);
                this.elements.secondaryImage.src = imageUrl;
                this.elements.secondaryImage.alt = this.adData.title || 'Товар';
            } else {
                this.elements.secondaryImage.style.display = 'none';
            }
        }
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
            `СОСТОЯНИЕ: ${conditionText.toUpperCase()}.`,
            this.adData.brand ? `БРЕНД: ${this.adData.brand.toUpperCase()}.` : null,
            this.adData.size ? `РАЗМЕР: ${this.adData.size.toUpperCase()}.` : null,
            this.adData.category ? `КАТЕГОРИЯ: ${this.getCategoryText(this.adData.category).toUpperCase()}.` : null
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
        const conditionMap = {
            'new': 'НОВОЕ',
            'like_new': 'ОТЛИЧНОЕ (КАК НОВОЕ)',
            'good': 'ХОРОШЕЕ',
            'satisfactory': 'УДОВЛЕТВОРИТЕЛЬНОЕ'
        };
        return conditionMap[condition] || condition || 'НЕ УКАЗАНО';
    }

    getCategoryText(category) {
        const categoryMap = {
            'clothing': 'Одежда',
            'shoes': 'Обувь',
            'accessories': 'Аксессуары'
        };
        return categoryMap[category] || category;
    }

    async showContacts() {
        if (!this.elements.contactModal) return;

        try {
            // Пока просто показываем модальное окно с заглушкой
            // В будущем здесь будет загрузка данных продавца
            if (this.elements.sellerName) {
                this.elements.sellerName.textContent = 'Имя: Не указано';
            }
            if (this.elements.sellerPhone) {
                this.elements.sellerPhone.textContent = 'Телефон: Не указан';
            }
            if (this.elements.sellerEmail) {
                this.elements.sellerEmail.textContent = 'Email: Не указан';
            }

            this.elements.contactModal.classList.add('show');
        } catch (error) {
            console.error('❌ Ошибка загрузки контактов:', error);
            this.showError('Не удалось загрузить контакты продавца');
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

