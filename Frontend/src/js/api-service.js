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
            console.log(`🔄 API ${config.method || 'GET'} Request: ${url}`);
            
            const response = await fetch(url, config);
            
            console.log(`📨 Response: ${response.status} for ${endpoint}`);
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`);
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
        
        // РАБОЧИЙ ФОРМАТ: POST с query parameters в URL
        const queryParams = new URLSearchParams({
            email: credentials.email,
            password: credentials.password
        }).toString();
        
        const endpoint = `/auth/login?${queryParams}`;
        
        return this.request(endpoint, {
            method: 'POST'
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