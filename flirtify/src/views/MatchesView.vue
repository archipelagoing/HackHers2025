<script>
export default {
  methods: {
    match(){
      this.$router.push('/playlists');
    },
  },
};
</script>

<template>
    <main>
        <h2>We found music matches for you!</h2>
        <div class="match-container">
            <h2>Matching you with: User 1!</h2>  
            <h2>Shared artists: ... </h2>
            <h2>Shared genres: ...</h2>
            <h2>Your summary ...</h2>
            <button @click="match">Match</button>
            <button>Skip</button>   
        </div>
    </main>
</template>