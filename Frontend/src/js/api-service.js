// api-service.js - ИСПРАВЛЕННАЯ ВЕРСИЯ
console.log('✅ api-service.js loaded');

class ApiService {
    constructor() {
        this.BASE_URL = 'http://localhost:8000/api';
        this.token = localStorage.getItem('auth_token');
        console.log('🔧 ApiService created');
    }

    async request(endpoint, options = {}) {
        const url = `${this.BASE_URL}${endpoint}`;
        
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        if (this.token) {
            config.headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            console.log(`🔄 API Request: ${endpoint}`, config);
            
            const response = await fetch(url, config);
            
            const responseText = await response.text();
            console.log(`📨 Response status: ${response.status}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}. Details: ${responseText}`);
            }
            
            const data = responseText ? JSON.parse(responseText) : {};
            console.log(`✅ API Response: ${endpoint}`, data);
            return data;
            
        } catch (error) {
            console.error(`❌ API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // Auth endpoints
    async register(userData) {
        // ПРАВИЛЬНЫЙ ФОРМАТ: бекенд ожидает name
        const registerData = {
            name: userData.name,
            email: userData.email,
            phone: userData.phone || '',
            password: userData.password
        };
        
        console.log('📤 Sending registration:', registerData);
        
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(registerData)
        });
    }

    async login(credentials) {
        // УНИВЕРСАЛЬНЫЙ МЕТОД: пробуем разные форматы
        console.log('🔐 Attempting login...');
        
        const attempts = [
            {
                name: 'POST with JSON',
                request: () => this.request('/auth/login', {
                    method: 'POST',
                    body: JSON.stringify(credentials)
                })
            },
            {
                name: 'GET with query',
                request: () => {
                    const queryParams = new URLSearchParams(credentials).toString();
                    return this.request(`/auth/login?${queryParams}`, { method: 'GET' });
                }
            }
        ];
        
        for (let attempt of attempts) {
            try {
                console.log(`🔄 Trying: ${attempt.name}`);
                const result = await attempt.request();
                console.log(`✅ Success with: ${attempt.name}`);
                return result;
            } catch (error) {
                console.log(`❌ Failed with ${attempt.name}:`, error.message);
                continue;
            }
        }
        
        throw new Error('All login methods failed');
    }

    async logout() {
        return this.request('/auth/logout', {
            method: 'POST'
        });
    }

    async getCurrentUser() {
        return this.request('/auth/me');
    }

    async updateProfile(profileData) {
        return this.request('/auth/profile', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
    }

    async updateAvatar(avatarData) {
        return this.request('/auth/avatar', {
            method: 'PUT',
            body: JSON.stringify(avatarData)
        });
    }

    // Users endpoints
    async getAllUsers() {
        return this.request('/users');
    }

    async getUserById(userId) {
        return this.request(`/users/${userId}`);
    }

    // Token management
    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
        console.log('🔑 Token saved');
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('auth_token');
        console.log('🔑 Token cleared');
    }
}

// Глобальный экземпляр
window.apiService = new ApiService();
console.log('✅ ApiService ready');