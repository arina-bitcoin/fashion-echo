class OffersPage {
    constructor() {
        this.ads = [];
        this.isLoading = false;
        this.elements = {
            offersContainer: document.getElementById('offers')
        };
        
        this.init();
    }

    async init() {
        console.log('🔄 Инициализация страницы предложений');
        await this.loadOffers();
    }

    async loadOffers() {
        if (this.isLoading) return;
        
        try {
            this.isLoading = true;
            this.showLoading();
            
            console.log('📡 Загрузка объявлений с сервера...');
            const ads = await window.apiService.getAds({
                skip: 0,
                limit: 100
            });
            
            console.log('✅ Получено объявлений:', ads.length);
            this.ads = Array.isArray(ads) ? ads : [];
            
            this.renderOffers();
            
        } catch (error) {
            console.error('❌ Ошибка загрузки объявлений:', error);
            this.showError('Не удалось загрузить объявления. Попробуйте обновить страницу.');
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }

    showLoading() {
        if (!this.elements.offersContainer) return;
        
        this.elements.offersContainer.innerHTML = `
            <div class="loading-offers">
                <div class="loading-spinner"></div>
                <p>Загрузка объявлений...</p>
            </div>
        `;
    }

    hideLoading() {
        // Загрузка скрывается после рендера
    }

    showError(message) {
        if (!this.elements.offersContainer) return;
        
        this.elements.offersContainer.innerHTML = `
            <div style="text-align: center; padding: 40px 20px; color: var(--error-color);">
                <p>${message}</p>
                <button class="btn btn-primary" onclick="location.reload()" style="margin-top: 20px;">
                    Обновить страницу
                </button>
            </div>
        `;
    }

    renderOffers() {
        if (!this.elements.offersContainer) return;
        
        if (this.ads.length === 0) {
            this.elements.offersContainer.innerHTML = `
                <div style="text-align: center; padding: 40px 20px; color: var(--text-secondary);">
                    <p>Пока нет объявлений</p>
                </div>
            `;
            return;
        }

        // Очищаем контейнер
        this.elements.offersContainer.innerHTML = '';

        // Рендерим каждое объявление
        this.ads.forEach(ad => {
            const offerCard = this.createOfferCard(ad);
            this.elements.offersContainer.appendChild(offerCard);
        });
    }

    createOfferCard(ad) {
        const card = document.createElement('div');
        card.className = 'offer-card';
        card.style.cursor = 'pointer';
        
        // Обработчик клика - открываем карточку товара
        card.addEventListener('click', () => {
            window.location.href = `product.html?id=${ad.id}`;
        });

        // Получаем первое изображение или placeholder
        const imageUrl = this.getImageUrl(ad);
        const placeholderUrl = this.getPlaceholderImage();
        
        // Форматируем цену
        const priceText = ad.price && ad.price > 0 
            ? `${Math.round(ad.price)} ₽` 
            : 'Обмен';

        card.innerHTML = `
            <img src="${imageUrl}" alt="${ad.title || 'Товар'}" class="offer-image" 
                 onerror="this.onerror=null; this.src='${placeholderUrl}'">
            <div class="offer-details">
                <div class="offer-name">${this.escapeHtml(ad.title || 'Без названия')}</div>
                <div class="offer-price">${priceText}</div>
                ${ad.size ? `<div class="offer-size">Размер: ${this.escapeHtml(ad.size)}</div>` : ''}
            </div>
        `;

        return card;
    }

    getImageUrl(ad) {
        const images = ad.images || [];
        const baseUrl = 'http://localhost:8000/static/';
        
        if (images.length > 0) {
            return this.normalizeImageUrl(images[0], baseUrl);
        }
        
        return this.getPlaceholderImage();
    }

    getPlaceholderImage() {
        // SVG заглушка вместо внешнего сервиса
        const svg = `
            <svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">
                <rect width="300" height="300" fill="#F3E4D3"/>
                <text x="50%" y="45%" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" fill="#4B0505">Нет фото</text>
                <text x="50%" y="55%" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#6b7280">FASHIONECHO</text>
            </svg>
        `.trim().replace(/\s+/g, ' ');
        return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
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
        
        // Если путь содержит "file_storage/", убираем этот префикс
        if (cleanPath.startsWith('file_storage/')) {
            cleanPath = cleanPath.replace('file_storage/', '');
        }
        
        return `${baseUrl}${cleanPath}`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    // Ждем, пока api-service загрузится
    if (window.apiService) {
        window.offersPage = new OffersPage();
    } else {
        // Если api-service еще не загружен, ждем
        window.addEventListener('load', () => {
            window.offersPage = new OffersPage();
        });
    }
});
