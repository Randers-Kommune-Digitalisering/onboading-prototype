  <template>
    <div>
      <h2>Opret Opgave</h2>
      <form @submit.prevent="submitForm">
        <div>
          <label for="title">Title:</label>
          <input type="text" v-model="title" required />
        </div>
        <div>
          <label for="beskrivelse">Beskrivelse:</label>
          <input type="text" v-model="beskrivelse" required />
        </div>
        <div>
          <label for="ansvarlig">Ansvarlig:</label>
          <input type="text" v-model="ansvarlig" required />
        </div>
        <div>
          <label for="startdato">Startdato:</label>
          <input type="date" v-model="startdato" required />
        </div>
        <div>
          <label for="slutdato">Slutdato:</label>
          <input type="date" v-model="slutdato" required />
        </div>
        <div>
          <label for="result">Result:</label>
          <input type="checkbox" v-model="result" />
        </div>
        <div>
          <label for="timestamp">Timestamp:</label>
          <input type="datetime-local" v-model="timestamp" required />
        </div>
        <div>
          <label for="ForløbID">ForløbID:</label>
          <input type="text" v-model="ForløbID" />
        </div>
        <div>
          <label for="ForløbsskabelonID">Forløbsskabelon:</label>
          <select v-model="ForløbsskabelonID">
            <option v-for="skabelon in forloebsskabeloner" :key="skabelon.ForløbsskabelonID" :value="skabelon.ForløbsskabelonID">
              {{ skabelon.name }}
            </option>
          </select>
        </div>
        <button class="button button-outline" type="submit">Create Opgave</button>
      </form>
      <div v-if="message">{{ message }}</div>
    </div>
  </template>
  
  <script>
  import { getForloebsskabeloner } from '../../services/forløbsskabelonService';
  import { createOpgave } from '../../services/opgaveService';
  
  export default {
    data() {
      return {
        title: '',
        beskrivelse: '',
        ansvarlig: '',
        startdato: '',
        slutdato: '',
        result: false,
        timestamp: '',
        ForløbID: '',
        ForløbsskabelonID: '',
        forloebsskabeloner: [],
        message: ''
      };
    },
    async created() {
      try {
        const response = await getForloebsskabeloner();
        this.forloebsskabeloner = response.data;
      } catch (error) {
        this.message = 'Failed to load Forløbsskabeloner';
      }
    },
    methods: {
      async submitForm() {
        if (!this.ForløbID && !this.ForløbsskabelonID) {
          this.message = 'Either ForløbID or ForløbsskabelonID is required';
          return;
        }
  
        const data = {
          title: this.title,
          beskrivelse: this.beskrivelse,
          ansvarlig: this.ansvarlig,
          startdato: this.startdato,
          slutdato: this.slutdato,
          result: this.result,
          timestamp: this.timestamp
        };
  
        if (this.ForløbID) {
          data.ForløbID = this.ForløbID;
        } else if (this.ForløbsskabelonID) {
          data.ForløbsskabelonID = this.ForløbsskabelonID;
        }
  
        try {
          const response = await createOpgave(data);
          this.message = response.data.message;
          this.title = '';
          this.beskrivelse = '';
          this.ansvarlig = '';
          this.startdato = '';
          this.slutdato = '';
          this.result = false;
          this.timestamp = '';
          this.ForløbID = '';
          this.ForløbsskabelonID = '';
        } catch (error) {
          this.message = error.response.data.error;
        }
      }
    }
  };
  </script>