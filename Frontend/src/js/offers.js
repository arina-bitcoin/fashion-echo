class OffersPage {
    constructor() {
        this.ads = [];
        this.isLoading = false;
        this.currentFilters = {};
        this.elements = {
            offersContainer: document.getElementById('offers'),
            searchInput: document.getElementById('search-input'),
            toggleFiltersBtn: document.getElementById('toggle-filters-btn'),
            filtersModal: document.getElementById('filters-modal'),
            modalCloseFilters: document.getElementById('modal-close-filters'),
            filtersContent: document.getElementById('filters-content'),
            filterStatus: document.getElementById('filter-status'),
            filterType: document.getElementById('filter-type'),
            filterSort: document.getElementById('filter-sort'),
            filterMinPrice: document.getElementById('filter-min-price'),
            filterMaxPrice: document.getElementById('filter-max-price'),
            filterSize: document.getElementById('filter-size'),
            filterColor: document.getElementById('filter-color'),
            applyFiltersBtn: document.getElementById('apply-filters-btn'),
            clearFiltersBtn: document.getElementById('clear-filters-btn')
        };
        
        this.init();
    }

    async init() {
        console.log('🔄 Инициализация страницы предложений');
        this.attachEventListeners();
        await this.loadOffers();
    }

    attachEventListeners() {
        // Поиск
        if (this.elements.searchInput) {
            this.elements.searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.applyFilters();
                }
            });
            // Поиск при вводе с задержкой (debounce)
            let searchTimeout;
            this.elements.searchInput.addEventListener('input', () => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.applyFilters();
                }, 500);
            });
        }

        // Открытие модального окна фильтров
        if (this.elements.toggleFiltersBtn) {
            this.elements.toggleFiltersBtn.addEventListener('click', () => this.openFiltersModal());
        }

        // Закрытие модального окна
        if (this.elements.modalCloseFilters) {
            this.elements.modalCloseFilters.addEventListener('click', () => this.closeFiltersModal());
        }

        // Закрытие при клике вне модального окна
        if (this.elements.filtersModal) {
            this.elements.filtersModal.addEventListener('click', (e) => {
                if (e.target === this.elements.filtersModal) {
                    this.closeFiltersModal();
                }
            });
        }

        // Закрытие при нажатии Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.elements.filtersModal?.classList.contains('show')) {
                this.closeFiltersModal();
            }
        });

        // Применить фильтры
        if (this.elements.applyFiltersBtn) {
            this.elements.applyFiltersBtn.addEventListener('click', () => {
                this.applyFilters();
                this.closeFiltersModal();
            });
        }

        // Сбросить фильтры
        if (this.elements.clearFiltersBtn) {
            this.elements.clearFiltersBtn.addEventListener('click', () => {
                this.clearFilters();
                this.closeFiltersModal();
            });
        }
    }

    openFiltersModal() {
        if (this.elements.filtersModal) {
            this.elements.filtersModal.classList.add('show');
            document.body.style.overflow = 'hidden'; // Блокируем прокрутку фона
            if (this.elements.toggleFiltersBtn) {
                this.elements.toggleFiltersBtn.textContent = 'Фильтры ▲';
            }
        }
    }

    closeFiltersModal() {
        if (this.elements.filtersModal) {
            this.elements.filtersModal.classList.remove('show');
            document.body.style.overflow = ''; // Разблокируем прокрутку
            if (this.elements.toggleFiltersBtn) {
                this.elements.toggleFiltersBtn.textContent = 'Фильтры ▼';
            }
        }
    }

    collectFilters() {
        const filters = {};

        // Статус
        if (this.elements.filterStatus?.value) {
            filters.status = this.elements.filterStatus.value;
        }

        // Тип
        if (this.elements.filterType?.value) {
            filters.type = this.elements.filterType.value;
        }

        // Основные категории
        const mainCategories = Array.from(document.querySelectorAll('.filter-checkbox[data-filter="main_categories"]:checked'))
            .map(cb => cb.value);
        if (mainCategories.length > 0) {
            filters.main_categories = mainCategories;
        }

        // Подкатегории
        const subcategories = Array.from(document.querySelectorAll('.filter-checkbox[data-filter="subcategories"]:checked'))
            .map(cb => cb.value);
        if (subcategories.length > 0) {
            filters.subcategories = subcategories;
        }

        // Сезоны
        const seasons = Array.from(document.querySelectorAll('.filter-checkbox[data-filter="seasons"]:checked'))
            .map(cb => cb.value);
        if (seasons.length > 0) {
            filters.seasons = seasons;
        }

        // Состояние
        const conditions = Array.from(document.querySelectorAll('.filter-checkbox[data-filter="condition"]:checked'))
            .map(cb => cb.value);
        if (conditions.length > 0) {
            filters.condition = conditions;
        }

        // Цена
        if (this.elements.filterMinPrice?.value) {
            filters.min_price = parseFloat(this.elements.filterMinPrice.value);
        }
        if (this.elements.filterMaxPrice?.value) {
            filters.max_price = parseFloat(this.elements.filterMaxPrice.value);
        }

        // Размер
        if (this.elements.filterSize?.value?.trim()) {
            filters.sizes = [this.elements.filterSize.value.trim()];
        }

        // Цвет
        if (this.elements.filterColor?.value?.trim()) {
            filters.colors = this.elements.filterColor.value.trim().split(',').map(c => c.trim()).filter(c => c);
        }

        // Поиск
        if (this.elements.searchInput?.value?.trim()) {
            filters.search = this.elements.searchInput.value.trim();
        }

        // Сортировка
        if (this.elements.filterSort?.value) {
            filters.sort = this.elements.filterSort.value;
        }

        return filters;
    }

    async applyFilters() {
        this.currentFilters = this.collectFilters();
        await this.loadOffers();
    }

    clearFilters() {
        // Очищаем все поля
        if (this.elements.searchInput) this.elements.searchInput.value = '';
        if (this.elements.filterStatus) this.elements.filterStatus.value = '';
        if (this.elements.filterType) this.elements.filterType.value = '';
        if (this.elements.filterSort) this.elements.filterSort.value = 'newest';
        if (this.elements.filterMinPrice) this.elements.filterMinPrice.value = '';
        if (this.elements.filterMaxPrice) this.elements.filterMaxPrice.value = '';
        if (this.elements.filterSize) this.elements.filterSize.value = '';
        if (this.elements.filterColor) this.elements.filterColor.value = '';

        // Снимаем все чекбоксы
        document.querySelectorAll('.filter-checkbox').forEach(cb => {
            cb.checked = false;
        });

        this.currentFilters = {};
        this.loadOffers();
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

    async loadOffers() {
        if (this.isLoading) return;
        
        try {
            this.isLoading = true;
            this.showLoading();
            
            console.log('📡 Загрузка объявлений с сервера...', this.currentFilters);
            const ads = await window.apiService.getAds({
                skip: 0,
                limit: 100,
                ...this.currentFilters
            });
            
            console.log('✅ Получено объявлений:', ads.length);
            this.ads = Array.isArray(ads) ? ads : [];
            
            // Отладочная информация о первом объявлении
            if (this.ads.length > 0) {
                console.log('📋 Пример объявления:', {
                    id: this.ads[0].id,
                    title: this.ads[0].title,
                    images: this.ads[0].images,
                    imagesType: typeof this.ads[0].images,
                    isArray: Array.isArray(this.ads[0].images)
                });
            }
            
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
        let images = ad.images || [];
        const baseUrl = 'http://localhost:8000/static/';
        
        // Если images - это строка (JSON), парсим её
        if (typeof images === 'string') {
            try {
                images = JSON.parse(images);
            } catch (e) {
                console.warn('⚠️ Не удалось распарсить images как JSON:', e);
                images = [];
            }
        }
        
        // Убеждаемся, что images - это массив
        if (!Array.isArray(images)) {
            console.warn('⚠️ images не является массивом:', images);
            images = [];
        }
        
        // Фильтруем пустые значения
        images = images.filter(img => img && typeof img === 'string' && img.trim());
        
        if (images.length > 0) {
            const imageUrl = this.normalizeImageUrl(images[0], baseUrl);
            console.log('🖼️ Изображение для товара:', imageUrl);
            return imageUrl;
        }
        
        console.warn('⚠️ Нет изображений для товара:', ad.id, ad.title);
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
