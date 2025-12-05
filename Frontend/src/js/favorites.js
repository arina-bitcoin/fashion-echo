class Favorites {
    constructor() {
        this.items = [];
        this.elements = this.initializeElements();
        this.attachEventListeners();
        this.loadFavorites();
    }

    initializeElements() {
        return {
            favoritesItems: document.getElementById('cart-items'),
            emptyFavorites: document.getElementById('empty-cart'),
            continueShopping: document.getElementById('continue-shopping'),
            toast: document.getElementById('toast')
        };
    }

    attachEventListeners() {
        if (this.elements.continueShopping) {
            this.elements.continueShopping.addEventListener('click', () => {
                window.location.href = 'offers.html';
            });
        }
    }

    async loadFavorites() {
        try {
            // Проверяем авторизацию
            if (!window.apiService.isAuthenticated()) {
                this.showEmptyState('Для просмотра избранного необходимо войти в систему');
                return;
            }

            // Загружаем избранное с сервера
            this.items = await window.apiService.getFavorites();
            console.log('✅ Избранное загружено:', this.items);
            
            this.renderFavorites();
        } catch (error) {
            console.error('❌ Ошибка загрузки избранного:', error);
            this.showEmptyState('Не удалось загрузить избранное');
        }
    }

    renderFavorites() {
        if (this.items.length === 0) {
            this.showEmptyState();
            return;
        }

        this.elements.emptyFavorites.style.display = 'none';
        this.elements.favoritesItems.style.display = 'flex';

        this.elements.favoritesItems.innerHTML = this.items.map(item => {
            const imageUrl = this.getImageUrl(item);
            const price = item.price && item.price > 0 ? `${Math.round(item.price)} ₽` : 'Обмен';
            
            return `
                <div class="cart-item" data-id="${item.id}">
                    <img src="${imageUrl}" alt="${item.title}" class="item-image" onerror="this.src='data:image/svg+xml;charset=utf-8,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%27500%27 height=%27500%27%3E%3Crect width=%27500%27 height=%27500%27 fill=%27%23F3E4D3%27/%3E%3Ctext x=%2750%25%27 y=%2745%25%27 text-anchor=%27middle%27 font-family=%27Arial%27 font-size=%2732%27 fill=%27%234B0505%27%3EНет изображения%3C/text%3E%3C/svg%3E'">
                    <div class="item-details">
                        <div class="item-name">${item.title || 'Без названия'}</div>
                        ${item.size ? `<div class="item-size">Размер: ${item.size}</div>` : ''}
                        <div class="item-price">${price}</div>
                    </div>
                    <div class="item-controls">
                        <button class="btn btn-primary" onclick="favorites.viewItem(${item.id})" style="margin-right: 8px;">
                            Посмотреть
                        </button>
                        <button class="remove-btn" onclick="favorites.removeItem(${item.id})" title="Удалить из избранного">
                            ❤️
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    getImageUrl(item) {
        if (!item.images || item.images.length === 0) {
            return this.getPlaceholderImage();
        }

        const baseUrl = 'http://localhost:8000/static/';
        const imagePath = item.images[0].file_path || item.images[0];
        
        // Убираем начальный слэш и file_storage/ если есть
        let cleanPath = imagePath.startsWith('/') ? imagePath.slice(1) : imagePath;
        if (cleanPath.startsWith('file_storage/')) {
            cleanPath = cleanPath.replace('file_storage/', '');
        }
        
        return `${baseUrl}${cleanPath}`;
    }

    getPlaceholderImage() {
        const svg = `
            <svg width="500" height="500" xmlns="http://www.w3.org/2000/svg">
                <rect width="500" height="500" fill="#F3E4D3"/>
                <text x="50%" y="45%" text-anchor="middle" font-family="Arial, sans-serif" font-size="32" fill="#4B0505">Нет изображения</text>
                <text x="50%" y="55%" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" fill="#6b7280">FASHIONECHO</text>
            </svg>
        `.trim().replace(/\s+/g, ' ');
        return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
    }

    async removeItem(adId) {
        try {
            if (!window.apiService.isAuthenticated()) {
                this.showToast('Необходимо войти в систему', true);
                return;
            }

            await window.apiService.removeFromFavorites(adId);
            this.items = this.items.filter(item => item.id !== adId);
            this.renderFavorites();
            this.showToast('Товар удален из избранного');
        } catch (error) {
            console.error('❌ Ошибка удаления из избранного:', error);
            this.showToast('Не удалось удалить товар из избранного', true);
        }
    }

    viewItem(adId) {
        window.location.href = `product.html?id=${adId}`;
    }

    showEmptyState(message = null) {
        this.elements.favoritesItems.style.display = 'none';
        this.elements.emptyFavorites.style.display = 'block';
        
        if (message) {
            const emptyText = this.elements.emptyFavorites.querySelector('.empty-cart-text');
            if (emptyText) {
                emptyText.textContent = message;
            }
        }
    }

    showToast(message, isError = false) {
        // Создаем toast элемент, если его нет
        let toast = this.elements.toast;
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'toast';
            toast.className = 'toast';
            document.body.appendChild(toast);
            this.elements.toast = toast;
        }

        toast.textContent = message;
        toast.className = `toast ${isError ? 'error' : ''} show`;
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

// Инициализация избранного при загрузке страницы
let favorites;
document.addEventListener('DOMContentLoaded', () => {
    favorites = new Favorites();
});

