<template>
  <div class="login-container">
    <div class="login-content">
      <div v-if="errorDetails" class="error-overlay">
        <div class="error-card">
          <h3>Authentication Error</h3>
          <div class="error-code">Error Code: {{ errorDetails.code }}</div>
          <div class="error-message">{{ errorDetails.message }}</div>
          <div class="error-help">{{ errorDetails.help }}</div>
          <button @click="retryLogin" class="retry-button">
            Try Again
          </button>
        </div>
      </div>
      
      <div class="left-section">
        <img src="/flirtify.png" alt="Flirtify Logo" class="flirtify-logo">
        <h1>FLIRTIFY</h1>
        <p class="tagline">Where Music Meets Romance</p>
        <div class="features">
          <div class="feature">
            <i class="fas fa-music"></i>
            <div class="feature-text">
              <h3>Music-Based Matching</h3>
              <p>Find connections through shared musical tastes</p>
            </div>
          </div>
          <div class="feature">
            <i class="fas fa-heart"></i>
            <div class="feature-text">
              <h3>Meaningful Connections</h3>
              <p>Connect with people who share your vibe</p>
            </div>
          </div>
          <div class="feature">
            <i class="fas fa-headphones"></i>
            <div class="feature-text">
              <h3>Shared Experiences</h3>
              <p>Discover and share playlists together</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="right-section">
        <div class="login-card">
          <h2>Get Started</h2>
          <p class="subtitle">Connect with your Spotify account to find your musical matches</p>
          
          <button @click="handleLogin" class="login-button" :disabled="isLoading">
            <i class="fab fa-spotify"></i>
            {{ isLoading ? 'Connecting...' : 'Continue with Spotify' }}
          </button>
          
          <p class="terms">By continuing, you agree to our Terms of Service and Privacy Policy</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '../services/api';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

export default {
  setup() {
    const router = useRouter();
    const isLoading = ref(false);
    const errorDetails = ref(null);

    const ERROR_CODES = {
      NETWORK_ERROR: {
        code: 'AUTH_001',
        message: 'Unable to connect to authentication service',
        help: 'Please check your internet connection and try again'
      },
      SPOTIFY_ERROR: {
        code: 'AUTH_002',
        message: 'Failed to connect to Spotify',
        help: 'Please try again in a few moments'
      },
      INVALID_RESPONSE: {
        code: 'AUTH_003',
        message: 'Invalid response from authentication service',
        help: 'Please refresh the page and try again'
      },
      MISSING_CREDENTIALS: {
        code: 'AUTH_004',
        message: 'Missing authentication credentials',
        help: 'Please ensure Spotify integration is properly configured'
      }
    };

    function retryLogin() {
      errorDetails.value = null;
      handleLogin();
    }

    async function handleLogin() {
      isLoading.value = true;
      errorDetails.value = null;

      try {
        console.log('1. Starting login process in LoginView...');
        console.log('Current API URL:', api.defaults?.baseURL);
        const response = await api.spotifyLogin();
        console.log('2. Received auth URL from backend:', response);
        
        if (response.auth_url) {
          console.log('3. Redirecting to Spotify auth URL:', response.auth_url);
          window.location.href = response.auth_url;
        } else {
          console.error('3. Error: No auth_url in response:', response);
          errorDetails.value = ERROR_CODES.INVALID_RESPONSE;
          throw new Error('No auth URL received');
        }
      } catch (err) {
        console.error('Login Error Details:', {
          name: err.name,
          message: err.message,
          stack: err.stack,
          response: {
            status: err.response?.status,
            statusText: err.response?.statusText,
            data: err.response?.data,
            headers: err.response?.headers
          },
          request: {
            url: err.config?.url,
            method: err.config?.method,
            baseURL: err.config?.baseURL,
            headers: err.config?.headers
          }
        });

        if (!navigator.onLine) {
          errorDetails.value = ERROR_CODES.NETWORK_ERROR;
        } else if (err.message.includes('Network Error')) {
          errorDetails.value = {
            code: 'AUTH_005',
            message: 'Cannot connect to authentication server',
            help: 'Please verify that the backend server is running on port 8000'
          };
        } else if (err.response?.status === 500) {
          errorDetails.value = ERROR_CODES.SPOTIFY_ERROR;
        } else if (err.response?.data?.detail?.includes('credentials')) {
          errorDetails.value = ERROR_CODES.MISSING_CREDENTIALS;
        } else {
          errorDetails.value = {
            code: 'AUTH_999',
            message: `Error: ${err.message}`,
            help: 'Please try again or contact support if the problem persists'
          };
        }
      } finally {
        isLoading.value = false;
      }
    }

    return { handleLogin, isLoading, errorDetails, retryLogin };
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  width: 100vw;
  overflow-x: hidden;
  background: linear-gradient(135deg, #1DB954 0%, #191414 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.login-content {
  display: flex;
  width: 100%;
  height: 100vh;
  background: rgba(255, 255, 255, 0.95);
}

.left-section {
  flex: 1.5;
  padding: 4rem;
  background: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow-y: auto;
}

.right-section {
  flex: 1;
  background: linear-gradient(45deg, #1DB954, #191414);
  padding: 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow-y: auto;
}

.flirtify-logo {
  width: 80px;
  height: 80px;
  margin-bottom: 2rem;
}

h1 {
  font-size: 3rem;
  color: #191414;
  margin: 0;
  letter-spacing: 2px;
}

.tagline {
  font-size: 1.2rem;
  color: #666;
  margin: 1rem 0 3rem;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 600px;
}

.feature {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
}

.feature i {
  font-size: 1.5rem;
  color: #1DB954;
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 12px;
}

.feature-text h3 {
  margin: 0 0 0.5rem;
  color: #191414;
}

.feature-text p {
  margin: 0;
  color: #666;
  line-height: 1.4;
}

.login-card {
  width: 100%;
  text-align: center;
  color: white;
  max-width: 400px;
}

.login-card h2 {
  font-size: 2rem;
  margin: 0 0 1rem;
}

.login-card .subtitle {
  opacity: 0.9;
  margin-bottom: 2rem;
}

.login-button {
  width: 100%;
  padding: 1rem 2rem;
  border: none;
  border-radius: 500px;
  background: white;
  color: #191414;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: transform 0.2s;
}

.login-button:hover {
  transform: translateY(-2px);
}

.login-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.login-button i {
  font-size: 1.2rem;
}

.error-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.error-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  max-width: 400px;
  width: 90%;
  text-align: center;
}

.error-code {
  color: #ff4444;
  font-family: monospace;
  margin: 1rem 0;
}

.error-message {
  color: #333;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

.error-help {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.retry-button {
  background: #1DB954;
  color: white;
  border: none;
  padding: 0.8rem 2rem;
  border-radius: 500px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.retry-button:hover {
  background: #1ed760;
}

.terms {
  font-size: 0.8rem;
  opacity: 0.7;
  margin-top: 2rem;
}

@media (max-width: 1024px) {
  .login-content {
    flex-direction: column;
    height: auto;
    min-height: 100vh;
  }
  
  .left-section,
  .right-section {
    padding: 3rem;
    width: 100%;
  }
  
  .right-section {
    padding-top: 0;
  }
  
  .features {
    max-width: 100%;
  }
}

@media (max-width: 600px) {
  .left-section,
  .right-section {
    padding: 2rem;
  }
  
  h1 {
    font-size: 2.5rem;
  }
}
</style>
