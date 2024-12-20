<template>
  <div>
    <h2>Opret Opgave</h2>
    <form @submit.prevent="submitForm">
      <div>
        <label for="title">Opgave navn:</label>
        <input type="text" v-model="title" required />
      </div>
      <div>
        <label for="beskrivelse">Beskrivelse:</label>
        <input type="text" v-model="beskrivelse" required />
      </div>
      <div>
        <label for="ansvarlig">Ansvarlig:</label>
        <input type="text" v-model="ansvarligSearch" placeholder="Search ansvarlig names" />
        <select v-model="ansvarlig" required>
          <option v-for="ansvarlig in filteredAnsvarligNames" :key="ansvarlig" :value="ansvarlig">
            {{ ansvarlig }}
          </option>
        </select>
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
        <label for="result">Status på opgaven:</label>
        <input type="checkbox" v-model="result" />
      </div>
      <div>
        <label for="timestamp">Timestamp:</label>
        <input type="datetime-local" v-model="timestamp" required />
      </div>
      <div>
        <label for="ForløbID">Forløb:</label>
        <select v-model="ForløbID">
          <option v-for="forloeb in forloebs" :key="forloeb.ForløbID" :value="forloeb.ForløbID">
            {{ forloeb.name }}
          </option>
        </select>
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
import { getAllForloeb } from '../../services/forløbService';
import { createOpgave } from '../../services/opgaveService';
import { getAnvarligNames } from '../../services/userService';

export default {
  data() {
    return {
      title: '',
      beskrivelse: '',
      ansvarlig: '',
      ansvarligSearch: '',
      startdato: '',
      slutdato: '',
      result: false,
      timestamp: '',
      ForløbID: '',
      ForløbsskabelonID: '',
      forloebsskabeloner: [],
      forloebs: [],
      ansvarligNames: [],
      message: ''
    };
  },
  async created() {
    try {
      const skabelonResponse = await getForloebsskabeloner();
      this.forloebsskabeloner = skabelonResponse.data;

      const ansvarligResponse = await getAnvarligNames();
      this.ansvarligNames = ansvarligResponse.data.fullnames;

      const forloebResponse = await getAllForloeb();
      this.forloebs = forloebResponse.data;
    } catch (error) {
      this.message = 'Failed to load data';
    }
  },
  computed: {
    filteredAnsvarligNames() {
      return this.ansvarligNames.filter(ansvarlig =>
        ansvarlig.toLowerCase().includes(this.ansvarligSearch.toLowerCase())
      );
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