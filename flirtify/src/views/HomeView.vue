<script>
import TheWelcome from '../components/TheWelcome.vue'
import axios from 'axios';  // You'll need to install axios: npm install axios
import router from '../router/index.ts'
import { useRoute } from 'vue-router'; // Import useRoute
import { onMounted } from 'vue';

export default{
  setup(){
    let message = null;
    const route = useRoute(); // Get the route object

    onMounted(async () => {
      try {
        console.log('i work')
        const response = await axios.get('https://api.spotify.com/v1/me', {});
        // Process the data
        message = response.data;
        // console.log('this is home', data);
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
    <h1>Welcome User!</h1>
    <!-- <h2>Location: </h2> -->
    <h2>Your favorite genres</h2>
    <ul>
      <li>
        Taylor Swift
      </li>
      <li>
        Ed sheeran
      </li>
    </ul>
    <router-link to="/matches">Find music matches</router-link>
  </main>
</template>
