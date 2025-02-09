import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor to include auth token
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
      // Test backend connection first
      try {
        const healthCheck = await apiClient.get('/health');
        console.log('Backend health check:', healthCheck.data);
      } catch (healthError) {
        console.error('Backend health check failed:', healthError);
        throw new Error('Backend server not available');
      }

      console.log('Making request to /api/auth/login...');
      const response = await apiClient.get('/api/auth/login', { 
        withCredentials: true 
      });
      console.log('Login response:', response.data);
      if (!response.data.auth_url) {
        console.error('No auth_url in response:', response.data);
        throw new Error('Invalid response format');
      }
      return response.data;
    } catch (error) {
      const errorDetails = {
        name: error.name,
        message: error.message,
        isAxiosError: error.isAxiosError,
        response: {
          status: error.response?.status,
          data: error.response?.data,
          headers: error.response?.headers
        },
        request: error.request,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          baseURL: error.config?.baseURL
        }
      };
      console.error('Login error details:', errorDetails);
      throw error;
    }
  },

  async handleCallback(code) {
    try {
      console.log('Making callback request with code:', code);
      const response = await apiClient.get(`/api/auth/callback?code=${code}`);
      console.log('Callback response:', response.data);
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        console.log('Token stored in localStorage');
        return response.data;
      } else {
        console.error('No access token in response:', response.data);
        throw new Error('No access token received');
      }
    } catch (error) {
      console.error('Callback error:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      });
      throw error;
    }
  },

  // User endpoints
  async getUserProfile() {
    try {
      const response = await apiClient.get('/users/me');
      return response.data;
    } catch (error) {
      if (error.response?.status === 401) {
        window.location.href = '/login';
      }
      throw error;
    }
  },

  // Match endpoints
  async getMatches() {
    try {
      const response = await apiClient.get('/match/matches');
      console.log('Matches response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching matches:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      });
      throw error;
    }
  }
};