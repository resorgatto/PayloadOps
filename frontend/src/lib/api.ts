import axios from 'axios';

// Base API instance attached to the Django backend
export const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor to inject JWT token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Interceptor to handle 401 Unauthorized (e.g. token refresh logic would go here)
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        // Optionally add refresh token logic here
        if (error.response?.status === 401) {
            // localStorage.removeItem('access_token');
            // window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);
