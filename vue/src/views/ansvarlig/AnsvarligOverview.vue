<template>
    <div class="oversigt-container">
      <h2>Opgave Oversigt for {{ userFullName }}</h2>
      <table class="opgave-table">
        <thead>
          <tr>
            <th>OpgaveID</th>
            <th>Titel</th>
            <th>Beskrivelse</th>
            <th>Startdato</th>
            <th>Slutdato</th>
            <th>Resultat</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="opgave in filteredOpgaver" :key="opgave.OpgaveID">
            <td>{{ opgave.OpgaveID }}</td>
            <td>{{ opgave.title }}</td>
            <td>{{ opgave.beskrivelse }}</td>
            <td>{{ opgave.startdato }}</td>
            <td>{{ opgave.slutdato }}</td>
            <td>{{ opgave.result }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script>
  import { getOpgaver } from '../../services/opgaveService';
  import { onMounted, ref, computed } from 'vue';
  import keycloak from '@/keycloak'
  
  export default {
    setup() {
      const opgaver = ref([]);
      const userFullName = ref('No name');
      const userRole = ref('No role');
  
      const fetchOpgaver = async () => {
        try {
          const response = await getOpgaver();
          opgaver.value = response.data;
        } catch (error) {
          console.error('Error fetching opgaver:', error);
        }
      };
  
      onMounted(() => {
        if (keycloak.authenticated) {
          userFullName.value = keycloak.tokenParsed?.name || 'No name';
          fetchOpgaver();
        } else {
          console.warn('Keycloak not authenticated');
        }
      });
  
      const filteredOpgaver = computed(() => {
        return opgaver.value.filter(opgave => opgave.ansvarlig === userFullName.value);
      });
  
      return {
        opgaver,
        userFullName,
        userRole,
        filteredOpgaver
      };
    }
  };
  </script>
  
  <style scoped>
  .oversigt-container {
    padding: 20px;
  }
  
  .opgave-table {
    width: 100%;
    border-collapse: collapse;
  }
  
  .opgave-table th, .opgave-table td {
    border: 1px solid #ddd;
    padding: 8px;
  }
  
  .opgave-table th {
    background-color: #f2f2f2;
    text-align: left;
  }
  
  .opgave-table tr:nth-child(even) {
    background-color: #f9f9f9;
  }
  
  .opgave-table tr:hover {
    background-color: #ddd;
  }
  </style>