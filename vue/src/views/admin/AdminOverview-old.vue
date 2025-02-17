  <template>
    <div>
      <h1>Leder Oversigt</h1>
      <h2>Igangværende Forløb</h2>
      <ul>
        <li v-for="forloeb in ongoingForloeb" :key="forloeb.ForløbID" @click="toggleDetails(forloeb.ForløbID)">
          {{ forloeb.name }} - {{ formatDate(forloeb.startdate) }} til {{ formatDate(forloeb.enddate) }}
          <div v-if="selectedForloebID === forloeb.ForløbID">
            <p><strong>Leder:</strong> {{ forloeb.admin }}</p>
            <p><strong>Medarbejder DQ-nummer:</strong> {{ forloeb.userdq }}</p>
            <p><strong>Medarbejder Mail:</strong> {{ forloeb.usermail }}</p>
            <p><strong>Løsningsprocent:</strong> {{ forloeb.solutionPercentage }}%</p>
          </div>
        </li>
      </ul>
      <h2>Afsluttede Forløb</h2>
      <ul>
        <li v-for="forloeb in completedForloeb" :key="forloeb.ForløbID" @click="toggleDetails(forloeb.ForløbID)">
          {{ forloeb.name }} - {{ formatDate(forloeb.startdate) }} til {{ formatDate(forloeb.enddate) }}
          <div v-if="selectedForloebID === forloeb.ForløbID">
            <p><strong>Leder:</strong> {{ forloeb.admin }}</p>
            <p><strong>Medarbejder DQ-nummer:</strong> {{ forloeb.userdq }}</p>
            <p><strong>Medarbejder Mail:</strong> {{ forloeb.usermail }}</p>
            <p><strong>Løsningsprocent:</strong> {{ forloeb.solutionPercentage }}%</p>
          </div>
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  import { getAllForloeb } from '../../services/forløbService';
  import { getOpgaverByForloebIDAdmin } from '../../services/opgaveService';
  import keycloak from '@/keycloak';
  
  export default {
    data() {
      return {
        ongoingForloeb: [],
        completedForloeb: [],
        selectedForloebID: null,
        userFullName: ''
      };
    },
    async created() {
      if (keycloak.authenticated) {
        this.userFullName = keycloak.tokenParsed?.name || 'No name';
        try {
          const response = await getAllForloeb();
          const filteredForloeb = response.data.filter(f => f.admin === this.userFullName);
          const forloeb = await Promise.all(filteredForloeb.map(async f => {
            const opgaverResponse = await getOpgaverByForloebIDAdmin(f.ForløbID);
            const opgaver = opgaverResponse.data;
            const totalTasks = opgaver.length;
            const completedTasks = opgaver.filter(opg => opg.result === true).length;
            const solutionPercentage = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;
            return { ...f, solutionPercentage: solutionPercentage.toFixed(2) };
          }));
          this.ongoingForloeb = forloeb.filter(f => new Date(f.enddate) > new Date());
          this.completedForloeb = forloeb.filter(f => new Date(f.enddate) <= new Date());
        } catch (error) {
          console.error('Error fetching forløb:', error);
        }
      } else {
        console.warn('Keycloak not authenticated');
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