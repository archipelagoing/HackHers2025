import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

// Create axios instance with interceptors
const apiClient = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
});

apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
    // Auth endpoints
    async spotifyLogin() {
        try {
            console.log('Attempting Spotify login...');
            const response = await apiClient.get('/auth/login');
            console.log('Full login response:', {
                status: response.status,
                headers: response.headers,
                data: response.data
            });
            if (!response.data.auth_url) {
                throw new Error('No auth URL received from backend');
            }
            return response.data.auth_url;
        } catch (error) {
            console.error('Login error details:', {
                message: error.message,
                response: error.response?.data,
                status: error.response?.status,
                fullError: error
            });
            throw error;
        }
    },

    async handleCallback(code) {
        try {
            console.log('Processing callback with code:', code);
            const response = await apiClient.get(`/auth/callback?code=${code}`);
            console.log('Callback response:', response.data);
            return response.data;
        } catch (error) {
            console.error('Callback error:', error);
            throw error;
        }
    },

    // User endpoints
    async getUserProfile() {
        const response = await apiClient.get('/users/me');
        return response.data;
    },

    // Match endpoints
    async getMatches() {
        const response = await apiClient.get('/match/matches');
        return response.data;
    }
}; 