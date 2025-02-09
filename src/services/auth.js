import api from './api'

export default {
  async login() {
    const response = await api.get('/auth/login')
    return response.data.auth_url
  },
  
  // Add other auth methods as needed
} 