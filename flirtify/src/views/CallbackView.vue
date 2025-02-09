<template>
  <div class="callback">
    <div class="callback-content">
      <h2>{{ statusMessage }}</h2>
      
      <div v-if="error" class="error-details">
        <h3>Error Details:</h3>
        <pre>{{ error }}</pre>
        <button @click="retryLogin" class="retry-button">
          Try Again
        </button>
      </div>

      <div v-if="debugInfo" class="debug-info">
        <h3>Debug Information:</h3>
        <pre>{{ debugInfo }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../services/api';

export default {
  props: {
    code: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const router = useRouter();
    const statusMessage = ref('Connecting to Spotify...');
    const error = ref(null);
    const debugInfo = ref(null);

    async function retryLogin() {
      router.push('/login');
    }

    onMounted(async () => {
      try {
        console.log('CallbackView mounted with code:', props.code);
        debugInfo.value = {
          hasCode: !!props.code,
          codeLength: props.code?.length,
          timestamp: new Date().toISOString()
        };

        if (!props.code) {
          statusMessage.value = 'Missing authorization code';
          error.value = 'No Spotify authorization code found in URL';
          throw new Error('No authorization code found');
        }

        statusMessage.value = 'Exchanging code for access token...';
        console.log('Attempting to exchange code for token...');
        const tokenData = await api.handleCallback(props.code);
        console.log('Token exchange successful:', {
          hasAccessToken: !!tokenData.access_token,
          userId: tokenData.user_id
        });
        
        debugInfo.value = {
          ...debugInfo.value,
          hasAccessToken: !!tokenData.access_token,
          hasRefreshToken: !!tokenData.refresh_token,
          userId: tokenData.user_id
        };

        statusMessage.value = 'Storing authentication data...';
        localStorage.setItem('access_token', tokenData.access_token);
        console.log('Access token stored in localStorage');

        statusMessage.value = 'Authentication successful! Redirecting...';
        console.log('About to redirect to home...');
        router.push('/home').catch(err => {
          console.error('Navigation error:', err);
        });
      } catch (err) {
        console.error('Callback error:', err);
        statusMessage.value = 'Authentication failed';
        error.value = {
          message: err.message,
          response: err.response?.data,
          status: err.response?.status,
          stack: err.stack
        };
        debugInfo.value = {
          ...debugInfo.value,
          error: err.message,
          responseStatus: err.response?.status,
          responseData: err.response?.data
        };
      }
    });

    return { statusMessage, error, debugInfo, retryLogin };
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
  padding: 2rem;
}

.callback-content {
  background: rgba(0, 0, 0, 0.2);
  padding: 2rem;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
}

h2 {
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.error-details {
  margin-top: 2rem;
  padding: 1rem;
  background: rgba(255, 0, 0, 0.1);
  border-radius: 8px;
}

.error-details h3 {
  color: #ff4444;
  margin-bottom: 0.5rem;
}

.debug-info {
  margin-top: 2rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.debug-info h3 {
  margin-bottom: 0.5rem;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: monospace;
  font-size: 0.9rem;
  margin: 0.5rem 0;
}

.retry-button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #1DB954;
  border: none;
  border-radius: 500px;
  color: white;
  cursor: pointer;
  font-weight: 600;
}

.retry-button:hover {
  background: #1ed760;
}
</style> 