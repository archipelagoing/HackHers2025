<script>
import { ref, onMounted } from 'vue';
import { api } from '../services/api';

export default {
  setup() {
    const matches = ref([]);
    const loading = ref(true);
    const error = ref(null);

    async function fetchMatches() {
      try {
        const data = await api.getMatches();
        matches.value = data.matches;
      } catch (err) {
        error.value = 'Failed to load matches. Please try again.';
        console.error('Error:', err);
      } finally {
        loading.value = false;
      }
    }

    onMounted(() => {
      fetchMatches();
    });

    return { matches, loading, error };
  }
};
</script>

<template>
  <div class="matches">
    <div class="matches-container">
      <h1>Your Matches</h1>
      
      <div v-if="loading" class="loading">
        Finding your matches...
      </div>
      
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      
      <div v-else class="matches-grid">
        <div v-for="match in matches" :key="match.user_id" class="match-card">
          <div class="match-header">
            <img 
              :src="match.profile_image || '/default-avatar.png'" 
              :alt="match.username"
              class="profile-image"
            >
            <div class="match-info">
              <h3>{{ match.username }}</h3>
              <div class="match-percentage">{{ Math.round(match.match_score) }}% Match</div>
            </div>
          </div>
          
          <div class="match-details">
            <div v-if="match.shared_artists.length" class="shared-section">
              <h4>Shared Artists</h4>
              <div class="shared-items">
                <span v-for="artist in match.shared_artists.slice(0,3)" :key="artist">
                  {{ artist }}
                </span>
                <span v-if="match.shared_artists.length > 3" class="more-count">
                  +{{ match.shared_artists.length - 3 }} more
                </span>
              </div>
            </div>
            
            <div v-if="match.shared_genres.length" class="shared-section">
              <h4>Shared Genres</h4>
              <div class="shared-items">
                <span v-for="genre in match.shared_genres.slice(0,3)" :key="genre">
                  {{ genre }}
                </span>
                <span v-if="match.shared_genres.length > 3" class="more-count">
                  +{{ match.shared_genres.length - 3 }} more
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.matches {
  min-height: 100vh;
  background: linear-gradient(180deg, 
    #121212 0%,
    rgba(18, 18, 18, 0.9) 25%,
    rgba(18, 18, 18, 0.8) 50%,
    rgba(18, 18, 18, 0.9) 75%,
    #121212 100%
  );
  color: white;
  padding: 2rem;
}

.matches-container {
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 2rem;
  padding-left: 1rem;
}

.matches-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
  padding: 1rem;
}

.match-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.match-card:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-4px);
}

.match-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.profile-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.match-info h3 {
  font-size: 1.4rem;
  font-weight: 600;
  margin: 0;
  color: white;
}

.match-percentage {
  color: #1DB954;
  font-weight: 600;
  font-size: 1.1rem;
  margin-top: 0.25rem;
}

.match-details {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  padding: 1rem;
}

.shared-section {
  margin-bottom: 1.5rem;
}

.shared-section:last-child {
  margin-bottom: 0;
}

.shared-section h4 {
  color: #b3b3b3;
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
  font-weight: 500;
}

.shared-items {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.shared-items span {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.4rem 0.8rem;
  border-radius: 500px;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}

.shared-items span:hover {
  background: rgba(255, 255, 255, 0.2);
}

.more-count {
  color: #b3b3b3;
  font-size: 0.85rem;
}

.loading {
  text-align: center;
  color: #b3b3b3;
  font-size: 1.2rem;
  padding: 4rem;
}

.error {
  color: #ff4444;
  text-align: center;
  padding: 4rem;
  background: rgba(255, 68, 68, 0.1);
  border-radius: 8px;
  margin: 2rem;
}

/* Spotify-style scrollbar */
::-webkit-scrollbar {
  width: 12px;
}

::-webkit-scrollbar-track {
  background: #121212;
}

::-webkit-scrollbar-thumb {
  background: #535353;
  border-radius: 8px;
}

::-webkit-scrollbar-thumb:hover {
  background: #7f7f7f;
}
</style>