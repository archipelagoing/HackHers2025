<template>
  <div class="callback">
    <h2>Logging you in...</h2>
  </div>
</template>

<script>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../services/api';

export default {
  setup() {
    const router = useRouter();

    onMounted(async () => {
      try {
        // Get code from URL
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        
        if (!code) {
          throw new Error('No authorization code found');
        }

        // Exchange code for token
        const tokenData = await api.handleCallback(code);
        
        // Store token
        localStorage.setItem('access_token', tokenData.access_token);
        if (tokenData.refresh_token) {
          localStorage.setItem('refresh_token', tokenData.refresh_token);
        }

        // Redirect to home
        router.push('/home');
      } catch (error) {
        console.error('Callback error:', error);
        router.push('/login');
      }
    });

    return {};
  }
}
</script>

<style scoped>
.callback {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1DB954 0%, #191414 100%);
  color: white;
}
</style> 