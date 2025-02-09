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
    <h1>Your Music Matches</h1>
    
    <div v-if="loading" class="loading">
      Finding your matches...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else class="matches-grid">
      <div v-for="match in matches" :key="match.user_id" class="match-card">
        <img 
          :src="match.profile_image || '/default-avatar.png'" 
          :alt="match.username"
          class="profile-image"
        >
        <h3>{{ match.username }}</h3>
        <div class="match-percentage">{{ Math.round(match.match_score) }}% Match</div>
        
        <div class="match-details">
          <div v-if="match.shared_artists.length" class="shared-section">
            <h4>Shared Artists</h4>
            <div class="shared-items">
              <span v-for="artist in match.shared_artists.slice(0,3)" :key="artist">
                {{ artist }}
              </span>
              <span v-if="match.shared_artists.length > 3">
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
              <span v-if="match.shared_genres.length > 3">
                +{{ match.shared_genres.length - 3 }} more
              </span>
            </div>
          </div>
          
          <div v-if="match.shared_tracks.length" class="shared-section">
            <h4>Shared Tracks</h4>
            <div class="shared-items">
              <span v-for="track in match.shared_tracks.slice(0,3)" :key="track">
                {{ track }}
              </span>
              <span v-if="match.shared_tracks.length > 3">
                +{{ match.shared_tracks.length - 3 }} more
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.matches {
  padding: 2rem;
}

.matches-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.match-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.profile-image {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 1rem;
}

.match-percentage {
  font-size: 1.4rem;
  color: #1DB954;
  font-weight: bold;
  margin: 0.5rem 0;
}

.match-details {
  text-align: left;
  margin-top: 1rem;
}

.shared-section {
  margin: 1rem 0;
}

.shared-section h4 {
  color: #666;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.shared-items {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.shared-items span {
  background: #f5f5f5;
  padding: 0.25rem 0.75rem;
  border-radius: 16px;
  font-size: 0.9rem;
}

.loading {
  text-align: center;
  color: #666;
  margin-top: 2rem;
}

.error {
  color: #dc3545;
  text-align: center;
  margin-top: 2rem;
}
</style>