<template>
  <div>
    <h2>Opret Ressource</h2>
    <form @submit.prevent="submitForm">
      <div>
        <label for="name">Name:</label>
        <input type="text" v-model="name" required />
      </div>
      <div>
        <label for="url">URL:</label>
        <input type="text" v-model="url" required />
      </div>
      <div>
        <label for="opgaveID">Opgave:</label>
        <select v-model="opgaveID">
          <option :value="null">None</option>
          <option v-for="opgave in opgaver" :key="opgave.OpgaveID" :value="opgave.OpgaveID">
            {{ opgave.title }}
          </option>
        </select>
      </div>
      <div>
        <label for="opgaveskabelonID">Opgaveskabelon:</label>
        <select v-model="opgaveskabelonID">
          <option :value="null">None</option>
          <option v-for="skabelon in opgaveskabeloner" :key="skabelon.OpgaveskabelonID" :value="skabelon.OpgaveskabelonID">
            {{ skabelon.title }}
          </option>
        </select>
      </div>
      <button class="button button-outline" type="submit">Create Ressource</button>
    </form>
    <div v-if="message">{{ message }}</div>
  </div>
</template>

<script>
import { createRessource, getOpgaver, getOpgaveskabeloner } from '../apiService';

export default {
  data() {
    return {
      name: '',
      url: '',
      opgaveID: null,
      opgaveskabelonID: null,
      opgaver: [],
      opgaveskabeloner: [],
      message: ''
    };
  },
  async created() {
    try {
      const [opgaverResponse, opgaveskabelonerResponse] = await Promise.all([
        getOpgaver(),
        getOpgaveskabeloner()
      ]);
      this.opgaver = opgaverResponse.data;
      this.opgaveskabeloner = opgaveskabelonerResponse.data;
    } catch (error) {
      this.message = 'Failed to load Opgaver or Opgaveskabeloner';
    }
  },
  methods: {
    async submitForm() {
      if (!this.opgaveID && !this.opgaveskabelonID) {
        this.message = 'Either OpgaveID or OpgaveskabelonID is required';
        return;
      }

      const data = {
        name: this.name,
        url: this.url
      };

      if (this.opgaveID) {
        data.OpgaveID = this.opgaveID;
      } else if (this.opgaveskabelonID) {
        data.OpgaveskabelonID = this.opgaveskabelonID;
      }

      try {
        const response = await createRessource(data);
        this.message = response.data.message;
        this.name = '';
        this.url = '';
        this.opgaveID = null;
        this.opgaveskabelonID = null;
      } catch (error) {
        this.message = error.response.data.error;
      }
    }
  }
};
</script>