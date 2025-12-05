class MyAdsPage {
    constructor() {
        this.ads = [];
        this.isLoading = false;
        this.elements = {
            content: document.getElementById('my-ads-content'),
            createAdBtn: document.getElementById('create-ad-btn')
        };
        
        this.init();
    }

    async init() {
        console.log('🔄 Инициализация страницы "Мои объявления"');
        
        // Проверяем авторизацию
        if (!window.apiService || !window.apiService.isAuthenticated()) {
            this.showError('Для просмотра объявлений необходимо войти в систему.');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
            return;
        }
        
        await this.loadAds();
    }

    async loadAds() {
        if (this.isLoading) return;
        
        try {
            this.isLoading = true;
            this.showLoading();
            
            console.log('📡 Загрузка объявлений пользователя...');
            const ads = await window.apiService.getUserAds();
            
            console.log('✅ Получено объявлений:', ads.length);
            this.ads = Array.isArray(ads) ? ads : [];
            
            this.renderAds();
            
        } catch (error) {
            console.error('❌ Ошибка загрузки объявлений:', error);
            this.showError('Не удалось загрузить объявления. Попробуйте обновить страницу.');
        } finally {
            this.isLoading = false;
        }
    }

    showLoading() {
        if (!this.elements.content) return;
        
        this.elements.content.innerHTML = `
            <div class="loading-offers">
                <div class="loading-spinner"></div>
                <p>Загрузка объявлений...</p>
            </div>
        `;
    }

    showError(message) {
        if (!this.elements.content) return;
        
        this.elements.content.innerHTML = `
            <div class="error-message">
                <p>${message}</p>
                <button class="btn btn-primary" onclick="location.reload()" style="margin-top: 20px;">
                    Обновить страницу
                </button>
            </div>
        `;
    }

    renderAds() {
        if (!this.elements.content) return;
        
        if (this.ads.length === 0) {
            this.elements.content.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📭</div>
                    <h2>У вас пока нет объявлений</h2>
                    <p>Создайте первое объявление, чтобы начать продавать или обмениваться одеждой</p>
                    <button class="btn btn-primary" onclick="window.location.href='create-ad.html'">
                        Создать объявление
                    </button>
                </div>
            `;
            return;
        }

        // Очищаем контейнер
        this.elements.content.innerHTML = '';

        // Рендерим каждое объявление
        this.ads.forEach(ad => {
            const adCard = this.createAdCard(ad);
            this.elements.content.appendChild(adCard);
        });
    }

    createAdCard(ad) {
        const card = document.createElement('div');
        card.className = 'my-ad-card';
        
        // Получаем первое изображение или placeholder
        const imageUrl = this.getImageUrl(ad);
        const placeholderUrl = this.getPlaceholderImage();
        
        let priceText;
        if (ad.type === 'buy') {
            priceText = 'Запрос на покупку';
        } else if (ad.price && ad.price > 0) {
            priceText = `${Math.round(ad.price)} ₽`;
        } else {
            priceText = 'Обмен';
        }
        
        // Статус активности
        const statusClass = ad.is_active ? 'active' : 'inactive';
        const statusText = ad.is_active ? 'Активно' : 'Неактивно';

        card.innerHTML = `
            <div class="ad-card-image">
                <img src="${imageUrl}" alt="${ad.title || 'Товар'}" 
                     onerror="this.onerror=null; this.src='${placeholderUrl}'">
                <div class="ad-status ${statusClass}">${statusText}</div>
            </div>
            <div class="ad-card-content">
                <h3 class="ad-card-title">${this.escapeHtml(ad.title || 'Без названия')}</h3>
                <div class="ad-card-price">${priceText}</div>
                <div class="ad-card-meta">
                    <span class="ad-meta-item">${this.escapeHtml(ad.category || 'Не указано')}</span>
                    ${ad.size ? `<span class="ad-meta-item">Размер: ${this.escapeHtml(ad.size)}</span>` : ''}
                </div>
                <div class="ad-card-actions">
                    <button class="btn btn-secondary btn-small" onclick="window.location.href='product.html?id=${ad.id}'">
                        Просмотр
                    </button>
                    <button class="btn btn-primary btn-small" onclick="window.myAdsPage.editAd(${ad.id})">
                        Редактировать
                    </button>
                    <button class="btn btn-danger btn-small" onclick="window.myAdsPage.deleteAd(${ad.id})" style="background: #ef4444; color: white;">
                        Удалить
                    </button>
                    <button class="btn btn-primary btn-small" onclick="window.myAdsPage.toggleAdStatus(${ad.id}, ${!ad.is_active})">
                        ${ad.is_active ? 'Деактивировать' : 'Активировать'}
                    </button>
                </div>
            </div>
        `;

        return card;
    }

    async toggleAdStatus(adId, newStatus) {
        try {
            console.log(`🔄 Изменение статуса объявления ${adId} на ${newStatus ? 'активно' : 'неактивно'}`);
            await window.apiService.updateAd(adId, { is_active: newStatus });
            this.showSuccess('Статус объявления успешно изменен');
            await this.loadAds();
        } catch (error) {
            console.error('❌ Ошибка изменения статуса:', error);
            this.showError('Не удалось изменить статус объявления');
        }
    }

    async editAd(adId) {
        // Переход на страницу редактирования с параметром id
        window.location.href = `create-ad.html?edit=${adId}`;
    }

    async deleteAd(adId) {
        // Подтверждение удаления
        const ad = this.ads.find(a => a.id === adId);
        const adTitle = ad ? ad.title : 'это объявление';
        
        if (!confirm(`Вы уверены, что хотите удалить объявление "${adTitle}"?\n\nЭто действие нельзя отменить.`)) {
            return;
        }

        try {
            console.log(`🗑️ Удаление объявления ${adId}`);
            await window.apiService.deleteAd(adId);
            this.showSuccess('Объявление успешно удалено');
            await this.loadAds();
        } catch (error) {
            console.error('❌ Ошибка удаления объявления:', error);
            this.showError('Не удалось удалить объявление');
        }
    }

    showSuccess(message) {
        // Простое уведомление об успехе
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10b981;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            font-weight: 500;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
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
        if (!imagePath || imagePath.includes('via.placeholder.com')) return this.getPlaceholderImage();
        
        if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
            return imagePath;
        }
        
        let cleanPath = imagePath.startsWith('/') ? imagePath.slice(1) : imagePath;
        
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
    if (window.apiService) {
        window.myAdsPage = new MyAdsPage();
    } else {
        window.addEventListener('load', () => {
            window.myAdsPage = new MyAdsPage();
        });
    }
});

