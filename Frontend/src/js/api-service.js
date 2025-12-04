// api-service.js - ФИНАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ
console.log('✅ api-service.js loaded');

class ApiService {
    constructor() {
        this.BASE_URL = 'http://localhost:8000/api';
        this.token = localStorage.getItem('auth_token');
        console.log('🔧 ApiService created with token:', !!this.token);
    }

    async request(endpoint, options = {}) {
        const url = `${this.BASE_URL}${endpoint}`;
        
        // Если body - FormData, не устанавливаем Content-Type (браузер сам добавит с boundary)
        const isFormData = options.body instanceof FormData;
        
        const config = {
            headers: {
                ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
                ...options.headers,
            },
            ...options,
        };

        if (this.token) {
            config.headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        // Если body - объект и не FormData, преобразуем в JSON
        if (options.body && !isFormData && typeof options.body === 'object' && !(options.body instanceof FormData)) {
            config.body = JSON.stringify(options.body);
        }

        try {
            console.log(`🔄 API ${config.method || 'GET'} Request: ${url}`);
            
            const response = await fetch(url, config);
            
            console.log(`📨 Response: ${response.status} for ${endpoint}`);
            
            if (!response.ok) {
                const errorText = await response.text();
                let errorMessage = errorText || response.statusText;
                
                // Пытаемся извлечь сообщение из JSON ответа
                try {
                    const errorJson = JSON.parse(errorText);
                    errorMessage = errorJson.detail || errorJson.message || errorMessage;
                } catch (e) {
                    // Если не JSON, используем текст как есть
                }
                
                const error = new Error(errorMessage);
                error.status = response.status;
                throw error;
            }
            
            const responseText = await response.text();
            const data = responseText ? JSON.parse(responseText) : {};
            return data;
            
        } catch (error) {
            console.error(`❌ API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // Auth endpoints - ФИНАЛЬНЫЕ РАБОЧИЕ МЕТОДЫ
    async register(userData) {
        const registerData = {
            name: userData.name,
            email: userData.email,
            phone: userData.phone || '',
            password: userData.password
        };
        
        console.log('📤 Registering user:', { ...registerData, password: '***' });
        
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(registerData)
        });
    }

    async login(credentials) {
        console.log('🔐 Logging in with:', { email: credentials.email, password: '***' });
        
        // // РАБОЧИЙ ФОРМАТ: POST с query parameters в URL
        // const queryParams = new URLSearchParams({
        //     email: credentials.email,
        //     password: credentials.password
        // }).toString();
        
        // const endpoint = `/auth/login?${queryParams}`;
        
        // return this.request(endpoint, {
        //     method: 'POST'
        // });
        // ПРАВИЛЬНЫЙ ФОРМАТ: POST с JSON в теле запроса
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({
                email: credentials.email,
                password: credentials.password
            })
        });
    }

    async logout() {
        console.log('🚪 Logging out...');
        
        try {
            const result = await this.request('/auth/logout', {
                method: 'POST'
            });
            this.clearToken();
            return result;
        } catch (error) {
            console.log('⚠️ Logout endpoint not available, clearing token locally');
            this.clearToken();
            return { message: 'Logged out locally' };
        }
    }

    async getCurrentUser() {
        console.log('👤 Getting current user...');
        
        // Используем работающий endpoint
        return this.request('/auth/me');
    }

    async updateProfile(profileData) {
        console.log('💾 Updating profile:', profileData);
        
        return this.request('/users/me', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
    }

// Avatar endpoints
    async uploadAvatar(file) {
        console.log('📤 Uploading avatar file:', file.name);
        
        const formData = new FormData();
        formData.append('file', file);
        
        const url = `${this.BASE_URL}/users/me/avatar`;
        
        const config = {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
            },
            body: formData,
        };

        try {
            console.log(`🔄 API POST Request: ${url}`);
            const response = await fetch(url, config);
            
            console.log(`📨 Response: ${response.status} for avatar upload`);
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }

            const data = await response.json();
        
        // Формируем полный URL для аватара
        if (data.avatar) {
            data.avatar_url = `http://localhost:8000/static/${data.avatar}`;
            console.log('✅ Avatar URL:', data.avatar_url);
        }
        
        return data;
            // return await response.json();
        } catch (error) {
            console.error('❌ Avatar upload error:', error);
            throw error;
        }
    }

    async deleteAvatar() {
        console.log('🗑️ Deleting avatar...');
        return this.request('/users/me/avatar', {
            method: 'DELETE'
        });
    }

    async deleteAccount() {
        console.log('🗑️ Deleting account...');
        return this.request('/users/me/delete', {
            method: 'DELETE'
        });
    }

    // Ad endpoints
    async getAds(params = {}) {
        console.log('📋 Getting ads with params:', params);
        const queryParams = new URLSearchParams();
        
        // Базовые параметры
        if (params.skip !== undefined) queryParams.append('skip', params.skip);
        if (params.limit !== undefined) queryParams.append('limit', params.limit);
        if (params.status) queryParams.append('status', params.status);
        if (params.type) queryParams.append('type', params.type);
        if (params.search) queryParams.append('search', params.search);
        if (params.sort) queryParams.append('sort', params.sort);
        
        // Ценовой диапазон
        if (params.min_price !== undefined) queryParams.append('min_price', params.min_price);
        if (params.max_price !== undefined) queryParams.append('max_price', params.max_price);
        
        // Массивы (категории, подкатегории, сезоны, состояния, размеры, цвета)
        if (params.main_categories && Array.isArray(params.main_categories)) {
            params.main_categories.forEach(cat => queryParams.append('main_categories', cat));
        }
        if (params.subcategories && Array.isArray(params.subcategories)) {
            params.subcategories.forEach(sub => queryParams.append('subcategories', sub));
        }
        if (params.seasons && Array.isArray(params.seasons)) {
            params.seasons.forEach(season => queryParams.append('seasons', season));
        }
        if (params.condition && Array.isArray(params.condition)) {
            params.condition.forEach(cond => queryParams.append('condition', cond));
        }
        if (params.sizes && Array.isArray(params.sizes)) {
            params.sizes.forEach(size => queryParams.append('sizes', size));
        }
        if (params.colors && Array.isArray(params.colors)) {
            params.colors.forEach(color => queryParams.append('colors', color));
        }
        
        // Обратная совместимость
        if (params.category) queryParams.append('category', params.category);
        
        const queryString = queryParams.toString();
        // Добавляем trailing slash, чтобы избежать редиректа
        const endpoint = queryString ? `/ads/?${queryString}` : '/ads/';
        return this.request(endpoint);
    }

    async getAd(adId) {
        console.log('📦 Getting ad:', adId);
        return this.request(`/ads/${adId}`);
    }

    async createAd(adData) {
        console.log('➕ Creating ad:', adData);
        return this.request('/ads/', {
            method: 'POST',
            body: JSON.stringify(adData)
        });
    }

    async getUserAds() {
        console.log('📋 Getting user ads');
        return this.request('/users/me/ads');
    }

    async uploadAdImage(file) {
        console.log('📤 Uploading ad image:', file.name);
        const formData = new FormData();
        formData.append('file', file);
        
        return this.request('/ads/upload-image', {
            method: 'POST',
            headers: {}, // Не устанавливаем Content-Type, браузер сам добавит с boundary
            body: formData
        });
    }

    async getUserPublicInfo(userId) {
        console.log('👤 Getting public user info:', userId);
        return this.request(`/users/${userId}/public`);
    }

    // Token management
    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
        localStorage.removeItem('fashioneco_current_user');
        console.log('🔑 Token saved');
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('auth_token');
        console.log('🔑 Token cleared');
    }

    isAuthenticated() {
    return !!this.token;
    }

    // 🔍 Поиск секонд-хендов
    async searchSecondhand(params = {}) {
        const query = new URLSearchParams(params).toString();
        const endpoint = query ? `/secondhand/?${query}` : '/secondhand/';

        console.log('🔍 searchSecondhand endpoint:', endpoint);

        return this.request(endpoint, {
            method: 'GET'
        });
    }
}

// Глобальный экземпляр
window.apiService = new ApiService();
console.log('✅ ApiService ready');