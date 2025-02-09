<template>
  <button @click="makeApiCall">Make API Call</button>
  <div v-if="responseMessage">{{ responseMessage }}</div>  <div v-if="errorMessage">{{ errorMessage }}</div> </template>

<script>
import axios from 'axios';  // You'll need to install axios: npm install axios
import router from '../router/index.ts'
import { useRouter } from 'vue-router';

export default {
  setup(){
    const router = useRouter();
  },
  data() {
    return {
      responseMessage: null,
      errorMessage: null
    };
  },
  methods: {
    async makeApiCall() {
      this.responseMessage = null; // Clear previous messages
      this.errorMessage = null;

      try {
        const response = await axios.post(
            'https://accounts.spotify.com/api/token',
            'grant_type=client_credentials&client_id=6a32b51f4b6a4a12b8d46b415ad98731&client_secret=6757642ea31a41b8bc1032e5d76aff36',
            {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });
        
        console.log('API Response:', response.data.access_token);
        router.push({ name: 'home'})
        // this.$router.push({ path: 'home', params: {token: response.access_token}})
        this.responseMessage = response; // Set the success message

      } catch (error) {
        console.error('API Error:', error);
        this.errorMessage = "An error occurred during the API call."; // Set the error message
        if (error) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          console.error("Response data:", error);
          console.error("Response status:", error);
          console.error("Response headers:", error);
          if (error && error) {
            this.errorMessage = error; // Display server error if available
          }
        } else if (error) {
          // The request was made but no response was received
          // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
          // http.ClientRequest in node.js
          console.error("Request:", error);
        } else {
          // Something happened in setting up the request that triggered an Error
          console.error("Error message:", error);
        }
      }
    }
  }
};
</script>