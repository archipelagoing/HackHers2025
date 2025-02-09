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

      <div class="content-grid">
        <!-- Top Artists -->
        <section class="card">
          <h2>Your Top Artists</h2>
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

      <section class="find-matches">
        <h2>Find Music Matches</h2>
        <router-link to="/matches" class="find-matches-btn">
          Find Matches
        </router-link>
      </section>
    </div>
  </div>
</template>

<style scoped>
.profile {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
  gap: 2rem;
}

.profile-image {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
}

.profile-info {
  flex: 1;
}

.stats {
  display: flex;
  gap: 1rem;
  color: #666;
}

.spotify-link {
  color: #1DB954;
  text-decoration: none;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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

.find-matches {
  text-align: center;
  margin-top: 2rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: #666;
}

.error {
  color: red;
  text-align: center;
  padding: 2rem;
}
</style>
