<template>
    <div>
      <h2>Opret Opgaveskabelon</h2>
      <form @submit.prevent="createOpgaveskabelon">
        <div>
          <label for="title">Title:</label>
          <input type="text" v-model="title" required />
        </div>
        <div>
          <label for="beskrivelse">Beskrivelse:</label>
          <input type="text" v-model="beskrivelse" required />
        </div>
        <div>
          <label for="startdato">Startdato:</label>
          <input type="datetime-local" v-model="startdato" required />
        </div>
        <div>
          <label for="slutdato">Slutdato:</label>
          <input type="datetime-local" v-model="slutdato" required />
        </div>
        <button class="button button-outline" type="submit">Opret Opgaveskabelon</button>
      </form>
      <div v-if="message">{{ message }}</div>
    </div>
  </template>
  
  <script>
  import { createOpgaveskabelon } from '../apiService';

export default {
  data() {
    return {
      title: '',
      beskrivelse: '',
      startdato: '',
      slutdato: '',
      message: ''
    };
  },
  methods: {
    async createOpgaveskabelon() {
      try {
        const response = await createOpgaveskabelon({
          title: this.title,
          beskrivelse: this.beskrivelse,
          startdato: this.startdato,
          slutdato: this.slutdato
        });
        this.message = response.data.message;
        this.title = '';
        this.beskrivelse = '';
        this.startdato = '';
        this.slutdato = '';
      } catch (error) {
        this.message = error.response.data.error;
      }
    }
  }
};
  </script>
