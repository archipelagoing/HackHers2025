<script>
import TheWelcome from '../components/TheWelcome.vue'
import axios from 'axios';  // You'll need to install axios: npm install axios
import router from '../router/index.ts'
import { onMounted } from 'vue';

export default{
  setup(){
    let message = null;

    onMounted(async () => {
      try {
        console.log('hola')
        const response = await fetch('https://api.spotify.com/v1/users/17awuac39bwx2gpnw2uxrqmnq/playlists', {});
        const data = await response.json();
        // Process the data
        console.log(data);
      } catch (error) {
        console.log('error', error)
      }
    });

    return { message };
  }
};
</script>

<template>
  <main>
    <h1>home</h1>
    <p>{{ message }}</p>
  </main>
</template>
