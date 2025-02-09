<script>
import { api } from '../services/api';
import { ref, onMounted } from 'vue';

export default {
  setup() {
    const currentMatch = ref(null);

    async function loadMatch() {
      try {
        const userId = localStorage.getItem('user_id');
        const matchData = await api.getMatches(userId);
        currentMatch.value = matchData;
      } catch (error) {
        console.error('Error loading match:', error);
      }
    }

    onMounted(loadMatch);

    return {
      currentMatch,
      handleMatch() {
        this.$router.push('/playlists');
      },
      skipMatch() {
        loadMatch();  // Load next match
      }
    };
  }
};
</script>

<template>
    <main>
        <h2>We found music matches for you!</h2>
        <div v-if="currentMatch" class="match-container">
            <h2>Matching you with: {{ currentMatch.username }}!</h2>  
            <h2>Shared artists: {{ currentMatch.shared_artists.join(', ') }}</h2>
            <h2>Shared genres: {{ currentMatch.shared_genres.join(', ') }}</h2>
            <h2>{{ currentMatch.compatibility_reasons.join(' ') }}</h2>
            <button @click="handleMatch">Match</button>
            <button @click="skipMatch">Skip</button>   
        </div>
    </main>
</template>