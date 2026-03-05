class MapPage {
    constructor() {
        this.map = null;
        this.ymaps = null;
        this.markers = [];
        this.searchInput = document.getElementById('shop-search');
        
        // Состояние карты
        this.isMapReady = false;
        this.isInitialized = false;
        this.lastLoadedBounds = null;
        
        // Дебаунсинг для загрузки данных
        this.loadDataTimeout = null;
        this.LOAD_DELAY = 500; // мс
        
        // Минимальное изменение границ для перезагрузки (в градусах)
        this.MIN_BOUNDS_CHANGE = 0.01;
        
        this.init();
    }

    async init() {
        console.log('🗺️ Initializing map page');
        await this.loadYandexMaps();
        this.initMap();
        this.attachEventListeners();
        
        // Загружаем данные только после полной инициализации
        setTimeout(() => {
            this.loadSecondhands();
        }, 100);
    }

    loadYandexMaps() {
        return new Promise((resolve, reject) => {
            if (window.ymaps) {
                window.ymaps.ready(() => {
                    this.ymaps = window.ymaps;
                    resolve();
                });
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://api-maps.yandex.ru/2.1/?lang=ru_RU';
            script.onload = () => {
                window.ymaps.ready(() => {
                    this.ymaps = window.ymaps;
                    console.log('✅ Yandex Maps loaded');
                    resolve();
                });
            };
            script.onerror = () => {
                console.error('❌ Failed to load Yandex Maps');
                reject(new Error('Failed to load Yandex Maps'));
            };
            document.head.appendChild(script);
        });
    }

    initMap() {
        // Инициализация карты с центром на Москве
        this.map = new this.ymaps.Map('yandex-map', {
            center: [37.6173, 55.7558], // [долгота, широта]
            zoom: 11,
            controls: ['zoomControl', 'fullscreenControl', 'geolocationControl']
        });
        
        // Настройка элементов управления
        this.map.controls.get('zoomControl').options.set('size', 'small');
        this.map.controls.get('fullscreenControl').options.set('size', 'small');
        this.map.controls.get('geolocationControl').options.set('size', 'small');

        // ЕДИНСТВЕННЫЙ обработчик изменения границ с правильным дебаунсингом
        this.map.events.add('boundschange', () => {
            this.scheduleDataLoad();
        });

        // Обработчик кликов по карте
        this.map.events.add('click', (e) => {
            this.handleMapClick(e);
        });

        this.isMapReady = true;
        console.log('✅ Map initialized');
    }

    // Планирование загрузки данных с дебаунсингом
    scheduleDataLoad() {
        // Отменяем предыдущую запланированную загрузку
        if (this.loadDataTimeout) {
            clearTimeout(this.loadDataTimeout);
        }

        // Планируем новую загрузку через задержку
        this.loadDataTimeout = setTimeout(() => {
            this.loadSecondhands();
        }, this.LOAD_DELAY);
    }

    // Проверка, нужно ли перезагружать данные
    shouldReloadData() {
        if (!this.lastLoadedBounds) {
            return true; // Первая загрузка
        }

        const currentBounds = this.getMapBounds();
        const lastBounds = this.lastLoadedBounds;

        // Проверяем, изменились ли границы значительно
        const latDiff = Math.abs(currentBounds.ne_lat - lastBounds.ne_lat) + 
                      Math.abs(currentBounds.sw_lat - lastBounds.sw_lat);
        const lngDiff = Math.abs(currentBounds.ne_lng - lastBounds.ne_lng) + 
                      Math.abs(currentBounds.sw_lng - lastBounds.sw_lng);

        return (latDiff > this.MIN_BOUNDS_CHANGE || lngDiff > this.MIN_BOUNDS_CHANGE);
    }

    attachEventListeners() {
        if (this.searchInput) {
            this.searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.searchSecondhands();
                }
            });
            
            // Поиск при вводе с задержкой
            let searchTimeout;
            this.searchInput.addEventListener('input', () => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.searchSecondhands();
                }, 500);
            });
        }
    }

    async searchSecondhands() {
        const searchQuery = this.searchInput?.value.trim();
        if (!searchQuery) {
            await this.loadSecondhands();
            return;
        }

        try {
            console.log('🔍 Searching secondhands:', searchQuery);
            const response = await window.apiService.getSecondhands({ search: searchQuery });
            const secondhands = response.items || response || [];
            this.updateMapMarkers(secondhands);
        } catch (error) {
            console.error('❌ Error searching secondhands:', error);
        }
    }

    async loadSecondhands() {
        if (!this.isMapReady) {
            console.log('⏳ Map not ready, skipping data load');
            return;
        }

        // Проверяем, нужно ли перезагружать данные
        if (!this.shouldReloadData()) {
            console.log('📊 Boundaries haven\'t changed significantly, skipping reload');
            return;
        }

        try {
            console.log('📡 Loading secondhands for map');
            const bounds = this.getMapBounds();
            console.log('🗺️ Current map bounds:', bounds);
            
            const secondhands = await window.apiService.getSecondhandsForMap(bounds);
            console.log('✅ Loaded secondhands:', Array.isArray(secondhands) ? secondhands.length : 'not an array');
            
            if (!Array.isArray(secondhands)) {
                console.error('❌ Expected array, got:', typeof secondhands, secondhands);
                return;
            }
            
            // Сохраняем текущие границы
            this.lastLoadedBounds = { ...bounds };
            
            this.updateMapMarkers(secondhands);
            
            // Автоматическое позиционирование ТОЛЬКО при первой загрузке
            if (!this.isInitialized && secondhands.length > 0) {
                this.fitMapToBounds(secondhands);
                this.isInitialized = true;
            }
            
        } catch (error) {
            console.error('❌ Error loading secondhands:', error);
        }
    }

    // Автоматическое позиционирование карты (только при первой загрузке)
    fitMapToBounds(secondhands) {
        const coordinates = secondhands
            .filter(s => s.latitude && s.longitude)
            .map(s => [s.latitude, s.longitude]);
        
        if (coordinates.length === 0) return;

        console.log('🎯 Fitting map to bounds (initial load only)');
        
        // Используем setBounds без обработчиков событий
        this.map.setBounds(
            this.ymaps.util.bounds.fromPoints(coordinates), 
            {
                checkZoomRange: true,
                duration: 500
            }
        );
    }

    getMapBounds() {
        const bounds = this.map.getBounds();
        // Яндекс карты возвращают [[sw_lng, sw_lat], [ne_lng, ne_lat]]
        const [[sw_lng, sw_lat], [ne_lng, ne_lat]] = bounds;
        
        return {
            ne_lat: ne_lat,
            ne_lng: ne_lng,
            sw_lat: sw_lat,
            sw_lng: sw_lng
        };
    }

    updateMapMarkers(secondhands) {
        console.log(`🗺️ Updating map markers. Total: ${secondhands.length}`);
        
        // Очищаем карту
        this.map.geoObjects.removeAll();

        // Добавляем новые метки
        secondhands.forEach((shop, index) => {
            if (!shop.latitude || !shop.longitude) return;

            console.log(`📌 Adding marker ${index + 1}: ${shop.name}`);
            
            const coordinates = [shop.latitude, shop.longitude];
            const placemark = this.createPlacemark(shop, coordinates);
            
            this.map.geoObjects.add(placemark);
        });

        console.log(`✅ Added ${this.map.geoObjects.getLength()} markers to map`);
    }

    createPlacemark(shop, coordinates) {
        const hintContent = this.createHintContent(shop);
        
        const placemark = new this.ymaps.Placemark(
            coordinates,
            {
                balloonContentHeader: `<b>${this.escapeHtml(shop.name)}</b>`,
                balloonContentBody: this.createBalloonContent(shop),
                hintContent: hintContent
            },
            {
                preset: 'islands#redDotIcon',
                openBalloonOnClick: false,
                hintOpenTimeout: 150,
                hintCloseTimeout: 200
            }
        );

        // Обработчики событий метки
        this.attachPlacemarkEvents(placemark, shop);
        
        return placemark;
    }

    createHintContent(shop) {
        return `
            <div style="
                padding: 10px 14px;
                font-size: 14px;
                line-height: 1.5;
                background: linear-gradient(135deg, #FFF8EF 0%, #F3E4D3 100%);
                border: 2px solid #4B0505;
                border-radius: 12px;
                box-shadow: 0 4px 16px rgba(75, 5, 5, 0.15);
                min-width: 200px;
                max-width: 280px;
                font-family: system-ui, -apple-system, sans-serif;
            ">
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    margin-bottom: 6px;
                ">
                    <strong style="
                        color: #4B0505;
                        font-size: 15px;
                        font-weight: 700;
                    ">${this.escapeHtml(shop.name)}</strong>
                </div>
                <div style="
                    display: flex;
                    align-items: flex-start;
                    gap: 6px;
                    color: #6b7280;
                    font-size: 12px;
                ">
                    <span style="color: #4B0505;">📍</span>
                    <span>${this.escapeHtml(shop.address || 'Адрес не указан')}</span>
                </div>
            </div>
        `;
    }

    createBalloonContent(shop) {
        return `
            <div style="padding: 8px 0;">
                <div style="margin-bottom: 8px;">
                    <strong>Адрес:</strong> ${this.escapeHtml(shop.address || 'Не указан')}
                </div>
                ${shop.phone ? `<div style="margin-bottom: 8px;"><strong>Телефон:</strong> ${this.escapeHtml(shop.phone)}</div>` : ''}
                <button class="btn-secondhand-link" data-shop-id="${shop.id}" 
                        style="padding: 8px 16px; background: #4B0505; color: white; border: none; border-radius: 8px; cursor: pointer; margin-top: 8px; width: 100%;">
                    Подробнее
                </button>
            </div>
        `;
    }

    attachPlacemarkEvents(placemark, shop) {
        // Наведение мыши - открываем балун
        placemark.events.add('mouseenter', () => {
            placemark.balloon.open();
        });
        
        // Клик по метке - переход на страницу
        placemark.events.add('click', (e) => {
            console.log(`🖱️ Clicked on marker: ${shop.name}`);
            e.stopPropagation();
            this.navigateToShop(shop.id);
        });
        
        // Обработчик открытия балуна
        placemark.events.add('balloonopen', () => {
            setTimeout(() => {
                const btn = document.querySelector(`.btn-secondhand-link[data-shop-id="${shop.id}"]`);
                if (btn) {
                    btn.onclick = (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        this.navigateToShop(shop.id);
                    };
                }
            }, 100);
        });

        // Сохраняем ID в свойствах для глобального обработчика
        placemark.properties.set('shopId', shop.id);
    }

    handleMapClick(e) {
        const target = e.get('target');
        
        // Проверяем клик по метке через target
        if (target && target.properties) {
            const shopId = target.properties.get('shopId');
            if (shopId) {
                console.log(`🖱️ Clicked on marker via target: ${shopId}`);
                this.navigateToShop(shopId);
                return;
            }
        }
        
        // Если клик не по метке - просто логируем
        console.log('🖱️ Clicked on map');
    }

    navigateToShop(shopId) {
        console.log(`📍 Navigating to secondhand: ${shopId}`);
        window.location.href = `secondhand.html?id=${shopId}`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('yandex-map')) {
        window.mapPage = new MapPage();
    }
});