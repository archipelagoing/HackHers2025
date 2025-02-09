import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null,
    user: null,
  }),

  actions: {
    setToken(token) {
      this.token = token;
    },

    setUser(user) {
      this.user = user;
    },

    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('access_token');
    },

    isAuthenticated() {
      return !!this.token;
    }
  },

  persist: true  // This will persist the store to localStorage
}); 