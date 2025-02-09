<template>
  <div>Processing login...</div>
</template>

<script>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import auth from '../services/auth'

export default {
  setup() {
    const router = useRouter()

    onMounted(async () => {
      // Handle Spotify callback
      // You'll need to implement this based on your auth flow
      try {
        // Process the callback
        // Redirect to appropriate page
        router.push('/')
      } catch (error) {
        console.error('Auth error:', error)
      }
    })
  }
}
</script> 