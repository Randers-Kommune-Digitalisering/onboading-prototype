<template>
  <div id="app">
    <h1>Vue-Python Template</h1>
    <div v-if="backendData">
      <h2>Data from Python Server:</h2>
      <p>{{ backendData }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      backendData: null
    }
  },
  mounted() {
    fetch('/api/example')
      .then(response => {
        if (response.headers.get('content-type')?.includes('application/json')) {
          return response.json();
        } else {
          return response.text();
        }
      })
      .then(data => {
        this.backendData = data;
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>