<template>
  <div class="callback-container">
    <div v-if="isLoading" class="loading">
      Connecting to Spotify...
    </div>
    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { api } from '../services/api';

export default {
  setup() {
    const route = useRoute();
    const router = useRouter();
    const authStore = useAuthStore();
    const isLoading = ref(true);
    const error = ref(null);

    onMounted(async () => {
      const code = route.query.code;
      if (!code) {
        error.value = 'No authorization code received';
        isLoading.value = false;
        return;
      }

      try {
        const userData = await api.handleCallback(code);
        authStore.setUser(userData);
        router.push('/home');
      } catch (err) {
        error.value = 'Failed to complete authentication';
        console.error('Callback error:', err);
      } finally {
        isLoading.value = false;
      }
    });

    return { isLoading, error };
  }
};
</script> 