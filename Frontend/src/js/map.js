class MapPage {
    constructor() {
        this.map = null;
        this.ymaps = null;
        this.markers = [];
        this.searchInput = document.getElementById('shop-search');
        this.geoObjectsClickHandlerAdded = false;
        this.init();
    }

    async init() {
        console.log('🗺️ Initializing map page');
        await this.loadYandexMaps();
        this.initMap();
        this.attachEventListeners();
        await this.loadSecondhands();
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
            // Для локальной разработки можно использовать без API ключа
            // В продакшене нужно добавить свой API ключ: https://developer.tech.yandex.ru/
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
        // Инициализация карты (центр на Москве)
        // Яндекс карты используют формат [долгота, широта]
        this.map = new this.ymaps.Map('yandex-map', {
            center: [37.6173, 55.7558], // Москва [долгота, широта]
            zoom: 11,
            controls: ['zoomControl', 'fullscreenControl', 'geolocationControl']
        });
        
        // Уменьшаем размер элементов управления для компактности
        this.map.controls.get('zoomControl').options.set('size', 'small');
        this.map.controls.get('fullscreenControl').options.set('size', 'small');
        this.map.controls.get('geolocationControl').options.set('size', 'small');

        // Обработчик изменения границ карты для загрузки новых меток
        this.map.events.add('boundschange', () => {
            this.updateMarkers();
        });
        
        // Глобальный обработчик кликов на карте для обработки кликов по меткам
        // Этот обработчик должен перехватывать клики по меткам
        this.map.events.add('click', (e) => {
            const target = e.get('target');
            const coords = e.get('coords');
            
            console.log('🖱️ Глобальный обработчик клика на карте');
            console.log('   target:', target);
            console.log('   target type:', typeof target);
            console.log('   target.constructor:', target?.constructor?.name);
            
            // Проверяем, кликнули ли по геообъекту (метке)
            // В Яндекс картах нужно проверить все geoObjects
            let shopId = null;
            
            // Проходим по всем меткам и проверяем, какая из них находится в точке клика
            this.map.geoObjects.each((geoObject) => {
                if (geoObject.properties) {
                    const objShopId = geoObject.properties.get('shopId');
                    if (objShopId) {
                        // Проверяем, находится ли клик вблизи этой метки
                        const geoCoords = geoObject.geometry.getCoordinates();
                        if (geoCoords) {
                            const distance = Math.sqrt(
                                Math.pow(coords[0] - geoCoords[0], 2) + 
                                Math.pow(coords[1] - geoCoords[1], 2)
                            );
                            // Если расстояние очень маленькое (клик по метке)
                            if (distance < 0.001) {
                                shopId = objShopId;
                                console.log(`   ✅ Найдена метка с shopId=${shopId} в точке клика`);
                            }
                        }
                    }
                }
            });
            
            if (shopId) {
                console.log(`📍 Переход на secondhand.html?id=${shopId}`);
                window.location.href = `secondhand.html?id=${shopId}`;
                return;
            }
            
            // Если не нашли метку, проверяем target напрямую
            if (target && target.properties) {
                shopId = target.properties.get('shopId');
                if (shopId) {
                    console.log(`✅ shopId из target.properties: ${shopId}`);
                    window.location.href = `secondhand.html?id=${shopId}`;
                    return;
                }
            }
            
            // Если клик не по метке, просто логируем
            console.log('   Клик не по метке (по карте)');
        });
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
        try {
            console.log('📡 Loading secondhands for map');
            const bounds = this.getMapBounds();
            console.log('🗺️ Map bounds:', bounds);
            const secondhands = await window.apiService.getSecondhandsForMap(bounds);
            console.log('✅ Loaded secondhands:', Array.isArray(secondhands) ? secondhands.length : 'not an array', secondhands);
            
            if (!Array.isArray(secondhands)) {
                console.error('❌ Expected array, got:', typeof secondhands, secondhands);
                return;
            }
            
            this.updateMapMarkers(secondhands);
        } catch (error) {
            console.error('❌ Error loading secondhands:', error);
            console.error('❌ Error details:', error.message, error.stack);
        }
    }

    getMapBounds() {
        const bounds = this.map.getBounds();
        // Яндекс карты возвращают bounds как [[sw_lng, sw_lat], [ne_lng, ne_lat]]
        const sw_coords = bounds[0];  // [sw_lng, sw_lat]
        const ne_coords = bounds[1];  // [ne_lng, ne_lat]
        
        // Извлекаем координаты в правильном порядке
        // Для России: lat ~55, lng ~37
        // Проверяем: если первая координата < 50, это долгота (для России)
        let sw_lat, sw_lng, ne_lat, ne_lng;
        
        if (sw_coords[0] < 50 && sw_coords[1] > 50) {
            // Формат: [[sw_lng, sw_lat], [ne_lng, ne_lat]] - правильный формат
            sw_lng = sw_coords[0];
            sw_lat = sw_coords[1];
            ne_lng = ne_coords[0];
            ne_lat = ne_coords[1];
        } else if (sw_coords[0] > 50 && sw_coords[1] < 50) {
            // Формат: [[sw_lat, sw_lng], [ne_lat, ne_lng]] - перепутанный
            sw_lat = sw_coords[0];
            sw_lng = sw_coords[1];
            ne_lat = ne_coords[0];
            ne_lng = ne_coords[1];
        } else {
            // По умолчанию считаем, что формат правильный: [lng, lat]
            sw_lng = sw_coords[0];
            sw_lat = sw_coords[1];
            ne_lng = ne_coords[0];
            ne_lat = ne_coords[1];
        }
        
        console.log(`🔍 Исходные bounds от Яндекс карт:`, bounds);
        console.log(`🔍 Распарсенные координаты: sw_lat=${sw_lat}, sw_lng=${sw_lng}, ne_lat=${ne_lat}, ne_lng=${ne_lng}`);
        
        // Финальная проверка: для России lat должна быть ~55, lng ~37
        // Если lat < 30 или > 60, значит координаты перепутаны
        if (sw_lat < 30 || sw_lat > 60) {
            console.error(`❌ ОШИБКА: sw_lat=${sw_lat} выходит за пределы России! Координаты перепутаны!`);
            console.error(`   Меняю местами lat и lng`);
            // Меняем местами
            [sw_lat, sw_lng] = [sw_lng, sw_lat];
            [ne_lat, ne_lng] = [ne_lng, ne_lat];
            console.log(`✅ Исправлено: sw_lat=${sw_lat}, sw_lng=${sw_lng}, ne_lat=${ne_lat}, ne_lng=${ne_lng}`);
        }
        
        return {
            ne_lat: ne_lat,  // широта северо-восточного угла
            ne_lng: ne_lng,  // долгота северо-восточного угла
            sw_lat: sw_lat,  // широта юго-западного угла
            sw_lng: sw_lng   // долгота юго-западного угла
        };
    }

    async updateMarkers() {
        await this.loadSecondhands();
    }

    updateMapMarkers(secondhands) {
        console.log(`🗺️ Обновляю метки на карте. Всего секондхендов: ${secondhands.length}`);
        
        // Удаляем старые метки
        this.map.geoObjects.removeAll();

        // Добавляем новые метки
        secondhands.forEach((shop, index) => {
            console.log(`\n📌 Секондхенд ${index + 1}/${secondhands.length}:`);
            if (!shop.latitude || !shop.longitude) return;

            // Проверка и исправление координат
            // Широта должна быть в диапазоне -90 до 90, долгота -180 до 180
            // Для России: широта ~55-60, долгота ~30-180
            let lat = shop.latitude;
            let lng = shop.longitude;
            
            // Если координаты выглядят перепутанными (широта > 90 или долгота > 180)
            // или если для России широта > долготы (что невозможно)
            if (Math.abs(lat) > 90 || Math.abs(lng) > 180) {
                console.warn(`⚠️ Подозрительные координаты для ${shop.name}: lat=${lat}, lng=${lng}`);
                // Пытаемся исправить, поменяв местами
                if (Math.abs(lat) <= 180 && Math.abs(lng) <= 90) {
                    console.log(`🔄 Исправляю координаты для ${shop.name}: меняю местами`);
                    [lat, lng] = [lng, lat];
                }
            }
            
            // Отладочный вывод координат
            console.log(`📍 ${shop.name}`);
            console.log(`   📍 Адрес: ${shop.address}`);
            console.log(`   📊 Координаты из API: latitude=${shop.latitude}, longitude=${shop.longitude}`);
            console.log(`   🔧 Используемые координаты: lat=${lat}, lng=${lng}`);

            // ВРЕМЕННОЕ ИСПРАВЛЕНИЕ: используем [lat, lng] вместо [lng, lat]
            // Яндекс карты обычно используют [долгота, широта], но похоже координаты перепутаны
            // Для России: если lat ~55, lng ~37, то [lat, lng] = [55, 37] может быть правильным
            const coordinates = [lat, lng]; // ВРЕМЕННО: используем [lat, lng]
            
            // Формируем содержимое подсказки (hint) при наведении с красивыми стилями
            const hintContent = `
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
                            letter-spacing: 0.02em;
                        ">${this.escapeHtml(shop.name)}</strong>
                    </div>
                    <div style="
                        display: flex;
                        align-items: flex-start;
                        gap: 6px;
                        color: #6b7280;
                        font-size: 12px;
                        line-height: 1.4;
                    ">
                        <span style="color: #4B0505; font-size: 14px;">📍</span>
                        <span>${this.escapeHtml(shop.address || 'Адрес не указан')}</span>
                    </div>
                </div>
            `;
            
            // Сохраняем ID для использования в обработчиках
            const shopId = shop.id;
            const shopName = shop.name;
            
            const placemark = new this.ymaps.Placemark(
                coordinates,
                {
                    balloonContentHeader: `<b>${this.escapeHtml(shop.name)}</b>`,
                    balloonContentBody: `
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
                    `,
                    balloonContentFooter: '',
                    hintContent: hintContent
                },
                {
                    preset: 'islands#redDotIcon',
                    openBalloonOnClick: false, // Не открываем балун при клике
                    // Настройки для подсказки при наведении
                    hintOpenTimeout: 150,
                    hintCloseTimeout: 200,
                    hintLayout: 'default#imageWithContent',
                    hintOffset: [0, -10]
                }
            );

            // Открываем балун при наведении на метку
            placemark.events.add('mouseenter', () => {
                console.log(`🖱️ Наведение на метку: ${shopName}`);
                placemark.balloon.open();
            });
            
            // Закрываем балун при уходе мыши (но не сразу, чтобы можно было кликнуть)
            placemark.events.add('mouseleave', () => {
                // Не закрываем сразу, чтобы можно было кликнуть на балун
                // Балун закроется автоматически при клике на карту
            });
            
            // Обработчик клика на метке - открываем страницу
            placemark.events.add('click', (e) => {
                console.log(`🖱️ КЛИК ПО МЕТКЕ: ${shopName} (ID: ${shopId})`);
                e.stopPropagation();
                window.location.href = `secondhand.html?id=${shopId}`;
            });
            
            // Обработчик клика на балуне - открываем страницу
            placemark.events.add('balloonopen', () => {
                console.log(`🎈 Балун открыт для: ${shopName}`);
                
                // Добавляем обработчик для кнопки "Подробнее" в балуне
                setTimeout(() => {
                    const btn = document.querySelector(`.btn-secondhand-link[data-shop-id="${shopId}"]`);
                    if (btn) {
                        btn.onclick = function(e) {
                            e.preventDefault();
                            e.stopPropagation();
                            console.log(`🔘 Клик по кнопке "Подробнее" для: ${shopName}`);
                            window.location.href = `secondhand.html?id=${shopId}`;
                            return false;
                        };
                        console.log(`✅ Обработчик кнопки добавлен для: ${shopName}`);
                    }
                    
                    // Также добавляем обработчик клика на весь балун
                    const balloon = document.querySelector('.ymaps-balloon');
                    if (balloon) {
                        balloon.style.cursor = 'pointer';
                        balloon.onclick = function(e) {
                            // Если клик не по кнопке, то переходим на страницу
                            if (!e.target.closest('.btn-secondhand-link')) {
                                console.log(`🔘 Клик по балуну для: ${shopName}`);
                                window.location.href = `secondhand.html?id=${shopId}`;
                            }
                        };
                    }
                }, 100);
            });

            // Сохраняем shopId в properties метки для глобального обработчика
            placemark.properties.set('shopId', shop.id);
            // Также сохраняем в data-атрибуте для надежности
            placemark.properties.set('data-shop-id', shop.id);
            console.log(`   🔧 shopId сохранен в properties: ${placemark.properties.get('shopId')}`);
            
            // Добавляем обработчик через geoObjects коллекцию (только один раз)
            if (!this.geoObjectsClickHandlerAdded) {
                this.map.geoObjects.events.add('click', (e) => {
                    const object = e.get('target');
                    console.log('🖱️ Клик через geoObjects.events, target:', object);
                    if (object && object.properties) {
                        const shopId = object.properties.get('shopId');
                        console.log('   shopId из object.properties:', shopId);
                        if (shopId) {
                            console.log(`📍 Переход на secondhand.html?id=${shopId}`);
                            window.location.href = `secondhand.html?id=${shopId}`;
                        }
                    }
                });
                this.geoObjectsClickHandlerAdded = true;
                console.log('✅ Обработчик geoObjects.events добавлен');
            }
            
            this.map.geoObjects.add(placemark);
            console.log(`   ✅ Метка добавлена на карту с shopId=${shop.id}`);
        });

        console.log(`\n✅ Всего добавлено меток на карту: ${this.map.geoObjects.getLength()}`);

        // Если есть точки, подстраиваем карту под них
        if (secondhands.length > 0) {
            const coordinates = secondhands
                .filter(s => s.latitude && s.longitude)
                .map(s => {
                    // ВРЕМЕННОЕ ИСПРАВЛЕНИЕ: используем [lat, lng] вместо [lng, lat]
                    return [s.latitude, s.longitude];
                });
            
            if (coordinates.length > 0) {
                this.map.setBounds(this.ymaps.util.bounds.fromPoints(coordinates), {
                    checkZoomRange: true,
                    duration: 300
                });
            }
        }
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

