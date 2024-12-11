<template>
    <div>
      <h1>Admin Oversigt</h1>
      <h2>Igangværende Forløb</h2>
      <ul>
        <li v-for="forloeb in ongoingForloeb" :key="forloeb.ForløbID" @click="toggleDetails(forloeb.ForløbID)">
          {{ forloeb.name }} - {{ formatDate(forloeb.startdate) }} til {{ formatDate(forloeb.enddate) }}
          <div v-if="selectedForloebID === forloeb.ForløbID">
            <p><strong>Admin:</strong> {{ forloeb.admin }}</p>
            <p><strong>User DQ:</strong> {{ forloeb.userdq }}</p>
            <p><strong>User Mail:</strong> {{ forloeb.usermail }}</p>
          </div>
        </li>
      </ul>
      <h2>Afsluttede Forløb</h2>
      <ul>
        <li v-for="forloeb in completedForloeb" :key="forloeb.ForløbID" @click="toggleDetails(forloeb.ForløbID)">
          {{ forloeb.name }} - {{ formatDate(forloeb.startdate) }} til {{ formatDate(forloeb.enddate) }}
          <div v-if="selectedForloebID === forloeb.ForløbID">
            <p><strong>Admin:</strong> {{ forloeb.admin }}</p>
            <p><strong>User DQ:</strong> {{ forloeb.userdq }}</p>
            <p><strong>User Mail:</strong> {{ forloeb.usermail }}</p>
          </div>
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  import { getAllForloeb } from '../../services/forløbService';
  
  export default {
    data() {
      return {
        ongoingForloeb: [],
        completedForloeb: [],
        selectedForloebID: null
      };
    },
    async created() {
      try {
        const response = await getAllForloeb();
        const forloeb = response.data;
        this.ongoingForloeb = forloeb.filter(f => new Date(f.enddate) > new Date());
        this.completedForloeb = forloeb.filter(f => new Date(f.enddate) <= new Date());
      } catch (error) {
        console.error('Error fetching forløb:', error);
      }
    },
    methods: {
      formatDate(date) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return new Date(date).toLocaleDateString(undefined, options);
      },
      toggleDetails(forloebID) {
        this.selectedForloebID = this.selectedForloebID === forloebID ? null : forloebID;
      }
    }
  };
  </script>
  
  <style scoped>
  h1 {
    margin-bottom: 20px;
  }
  h2 {
    margin-top: 20px;
  }
  ul {
    list-style-type: none;
    padding: 0;
  }
  li {
    margin-bottom: 10px;
    cursor: pointer;
  }
  li div {
    margin-top: 10px;
    padding-left: 20px;
  }
  </style>