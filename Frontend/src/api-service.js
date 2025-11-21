// api-service.js
class ApiService {
    constructor() {
        this.BASE_URL = 'http://localhost:8000/api'; // Ваш бекенд URL
        this.token = localStorage.getItem('auth_token');
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
        console.log(`📦 Request body:`, options.body);
        
        const response = await fetch(url, config);
        
        console.log(`📨 Response status: ${response.status}`);
        console.log(`📨 Response headers:`, Object.fromEntries(response.headers.entries()));
        
        // ПОЛУЧАЕМ ТЕКСТ ОТВЕТА В ЛЮБОМ СЛУЧАЕ
        const responseText = await response.text();
        console.log(`📨 Response body:`, responseText);
        
        if (!response.ok) {
            // Парсим JSON ошибки если возможно
            let errorDetails = responseText;
            try {
                const errorJson = JSON.parse(responseText);
                errorDetails = JSON.stringify(errorJson, null, 2);
            } catch (e) {
                // Оставляем как текст
            }
            
            throw new Error(`HTTP error! status: ${response.status}. Details: ${errorDetails}`);
        }
        
        // Парсим успешный ответ
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
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async login(credentials) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
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

    // Сохраняем токен
    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    }

    // Удаляем токен
    clearToken() {
        this.token = null;
        localStorage.removeItem('auth_token');
    }
}

// Глобальный экземпляр
window.apiService = new ApiService();