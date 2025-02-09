import { ref } from 'vue';
import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null);
  const isLoading = ref(false);
  const error = ref(null);

  function setUser(userData) {
    user.value = userData;
    localStorage.setItem('user_id', userData.spotify_id);
    localStorage.setItem('access_token', userData.access_token);
  }

  function clearUser() {
    user.value = null;
    localStorage.removeItem('user_id');
    localStorage.removeItem('access_token');
  }

  function isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }

  return { user, isLoading, error, setUser, clearUser, isAuthenticated };
}); 