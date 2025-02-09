<script>
import { api } from '../services/api';
import { ref, onMounted } from 'vue';

export default {
  setup() {
    const userData = ref(null);
    const error = ref(null);

    onMounted(async () => {
      try {
        const userId = localStorage.getItem('user_id');
        if (userId) {
          const data = await api.getUserProfile(userId);
          userData.value = data;
        }
      } catch (err) {
        error.value = err.message;
        console.error('Error fetching user data:', err);
      }
    });

    return { userData, error };
  }
};
</script>

<template>
  <main>
    <h1>Welcome {{ userData?.username || 'User' }}!</h1>
    <!-- <h2>Location: </h2> -->
    <div class="container-info">
      <div class="genres">
        <h2>Your favorite genres</h2>
        <ul>
          <li v-for="genre in userData?.top_genres" :key="genre">
            {{ genre }}
          </li>
        </ul>
      </div>
      <div class="artists">
        <h2>Your top artists</h2>
        <ul>
          <li v-for="artist in userData?.top_artists" :key="artist">
            {{ artist }}
          </li>
        </ul>
      </div>
    </div>
    
    <router-link to="/matches">Find music matches</router-link>
  </main>
</template>

<style>
div.container-info{
  display: flex;
  flex-direction: row;
}

ul{
  list-style: none;
}

li{
  display: flex;
  height: 60px;
  width: 280px;
  align-items: center;
  margin: 10px;
  border: 2px solid green;
  padding-left: 15px;
}
</style>
