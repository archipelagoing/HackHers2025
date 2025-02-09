<script>
import { ref, onMounted } from 'vue';
import { api } from '../services/api';

export default {
  setup() {
    const userData = ref(null);
    const loading = ref(true);
    const error = ref(null);

    async function fetchUserData() {
      try {
        loading.value = true;
        const data = await api.getUserProfile();
        userData.value = data;
      } catch (err) {
        error.value = 'Failed to load user data. Please try logging in again.';
        console.error('Error fetching user data:', err);
      } finally {
        loading.value = false;
      }
    }

    onMounted(() => {
      fetchUserData();
    });

    return { userData, loading, error };
  }
};
</script>

<template>
  <div class="home">
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="profile">
      <!-- Top Action Section -->
      <div class="top-actions">
        <router-link to="/matches" class="find-matches-btn">
          Find Music Matches
        </router-link>
      </div>

      <!-- Profile Header -->
      <div class="profile-header">
        <img 
          v-if="userData?.profile_image" 
          :src="userData.profile_image" 
          :alt="userData?.username"
          class="profile-image"
        >
        <div class="profile-info">
          <h1>Welcome {{ userData?.username }}</h1>
          <div class="stats">
            <span>{{ userData?.followers }} followers</span>
            <a :href="userData?.spotify_url" target="_blank" class="spotify-link">
              Open in Spotify
            </a>
          </div>
        </div>
      </div>

      <!-- AI Summary Card -->
      <section class="ai-summary-card">
        <h2>Your Music Personality</h2>
        <p>{{ userData?.ai_summary || "Based on your music taste, you're drawn to indie and dream pop with a touch of alternative rock. Your playlist choices suggest you appreciate introspective lyrics and atmospheric soundscapes, with artists like Japanese Breakfast and Beach House featuring prominently in your rotation." }}</p>
      </section>

      <div class="content-grid">
        <!-- Top Artists -->
        <section class="card">
          <h2>Top Artists</h2>
          <ul>
            <li v-for="artist in userData?.top_artists" :key="artist">
              {{ artist }}
            </li>
          </ul>
        </section>

        <!-- Top Tracks -->
        <section class="card">
          <h2>Your Top Tracks</h2>
          <ul>
            <li v-for="track in userData?.top_tracks" :key="track.name" class="track-item">
              <div class="track-info">
                <strong>{{ track.name }}</strong>
                <span>{{ track.artist }} • {{ track.album }}</span>
              </div>
              <audio v-if="track.preview_url" controls :src="track.preview_url"></audio>
            </li>
          </ul>
        </section>

        <!-- Genres -->
        <section class="card">
          <h2>Your Favorite Genres</h2>
          <ul class="genres-list">
            <li v-for="genre in userData?.top_genres" :key="genre">
              {{ genre }}
            </li>
          </ul>
        </section>

        <!-- Playlists -->
        <section class="card">
          <h2>Your Playlists</h2>
          <div class="playlists-grid">
            <div v-for="playlist in userData?.playlists" :key="playlist.name" class="playlist-card">
              <img 
                :src="playlist.image || '/default-playlist.png'" 
                :alt="playlist.name"
              >
              <h3>{{ playlist.name }}</h3>
              <span>{{ playlist.tracks }} tracks</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  min-height: 100vh;
  background: #121212;
  color: white;
  padding: 2rem;
}

.profile {
  max-width: 1200px;
  margin: 0 auto;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  margin-bottom: 2rem;
}

.profile-image {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 8px 24px rgba(0,0,0,0.5);
}

.profile-info h1 {
  font-size: 2.5rem;
  margin: 0;
  color: white;
}

.stats {
  display: flex;
  gap: 1rem;
  color: #b3b3b3;
  margin-top: 0.5rem;
}

.spotify-link {
  color: #1DB954;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.spotify-link:hover {
  color: #1ed760;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.card {
  background: #181818;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 8px 24px rgba(0,0,0,0.5);
  transition: background-color 0.3s;
}

.card:hover {
  background: #282828;
}

.card h2 {
  color: white;
  margin-bottom: 1rem;
}

.card ul {
  list-style: none;
  padding: 0;
}

.card li {
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 4px;
  margin-bottom: 0.5rem;
  transition: background-color 0.3s;
}

.card li:hover {
  background: rgba(255, 255, 255, 0.1);
}

.track-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.track-info {
  display: flex;
  flex-direction: column;
}

.playlists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.playlist-card {
  text-align: center;
}

.playlist-card img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.loading {
  text-align: center;
  color: #b3b3b3;
  font-size: 1.2rem;
  padding: 2rem;
}

.error {
  color: #ff4444;
  text-align: center;
  padding: 2rem;
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

/* Add these new styles */
.top-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 2rem;
  padding: 1rem;
}

.find-matches-btn {
  display: inline-block;
  background: #1DB954;
  color: white;
  padding: 1rem 2rem;
  border-radius: 500px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.2rem;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.find-matches-btn:hover {
  background: #1ed760;
  transform: scale(1.05);
}

.ai-summary-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
}

.ai-summary-card:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.ai-summary-card h2 {
  color: #1DB954;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.ai-summary-card p {
  color: #ffffff;
  line-height: 1.6;
  font-size: 1.1rem;
}

/* Remove the old find-matches section styles */
.find-matches {
  display: none;
}
</style>
