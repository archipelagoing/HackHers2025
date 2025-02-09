<template>
  <div class="login-container">
    <h1>Welcome to Flirtify</h1>
    <button 
      @click="handleLogin" 
      :disabled="isLoading"
      class="spotify-login-btn"
    >
      {{ isLoading ? 'Connecting...' : 'Login with Spotify' }}
    </button>
    <div v-if="error" class="error-message">
      {{ error }}
      <div v-if="detailedError" class="error-details">
        {{ detailedError }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { api } from '../services/api';

export default {
  setup() {
    const isLoading = ref(false);
    const error = ref(null);
    const detailedError = ref(null);

    async function handleLogin() {
      isLoading.value = true;
      error.value = null;
      detailedError.value = null;

      try {
        console.log('Starting login process...');
        const authUrl = await api.spotifyLogin();
        console.log('Auth URL received:', authUrl);
        if (!authUrl) {
          throw new Error('No auth URL received');
        }
        window.location.href = authUrl;
      } catch (err) {
        error.value = 'Failed to connect to Spotify. Please try again.';
        detailedError.value = `Error: ${err.message}. ${err.response?.data?.detail || ''}`;
        console.error('Login error:', err);
      } finally {
        isLoading.value = false;
      }
    }

    return { handleLogin, isLoading, error, detailedError };
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}

.spotify-login-btn {
  background: #1DB954;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 24px;
  font-size: 16px;
  cursor: pointer;
}

.spotify-login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-message {
  color: red;
  margin-top: 1rem;
}

.error-details {
  font-size: 0.8em;
  margin-top: 0.5rem;
  color: #666;
}
</style>