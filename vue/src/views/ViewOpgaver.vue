<template>
  <div>
    <form @submit.prevent="fetchOpgaver">
      <div>
        <label for="forloebID">ForløbID:</label>
        <input type="text" v-model="forloebID" />
      </div>
      <div>
        <label for="forloebsskabelonID">Forløbsskabelon:</label>
        <select v-model="forloebsskabelonID">
          <option v-for="skabelon in forloebsskabeloner" :key="skabelon.ForløbsskabelonID" :value="skabelon.ForløbsskabelonID">
            {{ skabelon.name }}
          </option>
        </select>
      </div>
      <button class="button button-outline" type="submit">Fetch Opgaver</button>
    </form>
    <div v-if="message">{{ message }}</div>
    <div v-if="opgaver.length">
      <h2>Opgaver</h2>
      <div class="opgaver-container">
        <div v-for="(opgave, index) in opgaver" :key="opgave.OpgaveID" class="opgave-card" @click="toggleDetails(index)">
          <h3>{{ opgave.title }}</h3>
          <p>{{ opgave.beskrivelse }}</p>
          <div v-if="opgave.showDetails" class="opgave-details">
            <p><i class="fas fa-user"></i> Ansvarlig: {{ opgave.ansvarlig }}</p>
            <p><i class="fas fa-calendar-alt"></i> Startdato: {{ formatDate(opgave.startdato) }}</p>
            <p><i class="fas fa-calendar-check"></i> Slutdato: {{ formatDate(opgave.slutdato) }}</p>
            <p><i class="fas fa-regular fa-hourglass-end"></i> Deadline: {{ calculateDeadline(opgave.startdato, opgave.slutdato) }} Timer</p>
            <p>
              <i class="fas fa-tasks"></i> Result:
              <input type="checkbox" v-model="opgave.result" @change="updateResult(opgave)" @click.stop />
            </p>
            <p><i class="fas fa-clock"></i> Timestamp: {{ formatDate(opgave.timestamp) }}</p>
            <h4>Resourcer:</h4>
            <ul>
              <li v-for="ressource in opgave.resourcer" :key="ressource.RessourceID">
                <a :href="formatUrl(ressource.url)" target="_blank" rel="noopener noreferrer"><i class="fas fa-link"></i> {{ ressource.name }}</a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getOpgaverByForloebID, getOpgaverByForloebsskabelonID, getForloebsskabelonerWithOpgavers, updateOpgaveResult } from '../apiService';

export default {
  data() {
    return {
      forloebID: '',
      forloebsskabelonID: '',
      forloebsskabeloner: [],
      opgaver: [],
      message: ''
    };
  },
  async created() {
    try {
      const response = await getForloebsskabelonerWithOpgavers();
      this.forloebsskabeloner = response.data;
    } catch (error) {
      this.message = 'Failed to load Forløbsskabeloner';
    }
  },
  methods: {
    async fetchOpgaver() {
      try {
        let response;
        if (this.forloebID) {
          response = await getOpgaverByForloebID(this.forloebID);
        } else if (this.forloebsskabelonID) {
          response = await getOpgaverByForloebsskabelonID(this.forloebsskabelonID);
        } else {
          this.message = 'Please provide either ForløbID or ForløbsskabelonID';
          return;
        }
        this.opgaver = response.data.map(opgave => ({ ...opgave, showDetails: false }));
        this.message = '';
      } catch (error) {
        this.message = error.response.data.error;
        this.opgaver = [];
      }
    },
    toggleDetails(index) {
      this.opgaver[index].showDetails = !this.opgaver[index].showDetails;
    },
    formatUrl(url) {
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        return `http://${url}`;
      }
      return url;
    },
    async updateResult(opgave) {
      try {
        await updateOpgaveResult(opgave.OpgaveID, opgave.result);
        this.message = 'Result updated successfully';
      } catch (error) {
        this.message = 'Failed to update result';
      }
    },
    calculateDeadline(startdato, slutdato) {
      const start = new Date(startdato);
      const end = new Date(slutdato);
      const diffInMs = end - start;
      const diffInHours = diffInMs / (1000 * 60 * 60);
      return diffInHours.toFixed(2);
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString('en-CA'); // 'en-CA' giver 'YYYY-MM-DD' formattet
    }
  }
};
</script>

<style scoped>
.opgaver-container {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.opgave-card {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 16px;
  width: 200px;
  cursor: pointer;
  transition: box-shadow 0.3s;
}

.opgave-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.opgave-details {
  margin-top: 16px;
}
</style>