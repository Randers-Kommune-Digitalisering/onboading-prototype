  <template>
    <div>
      <h2>Opret Forløbsskabelon</h2>
      <form @submit.prevent="submitForm">
        <div>
          <label for="name">Name:</label>
          <input type="text" v-model="form.name" required />
        </div>
        <div>
          <label for="varighed">Varighed:</label>
          <input type="datetime-local" v-model="form.varighed" required />
        </div>
        <button class="button button-outline" type="submit">Opret Forløbsskabelon</button>
      </form>
      <div v-if="message">{{ message }}</div>
    </div>
  </template>
  
  <script>
  import { createForloebsskabelon } from '../../services/forløbsskabelonService';
  
  export default {
    data() {
      return {
        form: {
          name: '',
          varighed: ''
        },
        message: ''
      };
    },
    methods: {
      async submitForm() {
        try {
          const response = await createForloebsskabelon({
            name: this.form.name,
            varighed: this.form.varighed
          });
          this.message = response.data.message;
          this.form.name = '';
          this.form.varighed = '';
        } catch (error) {
          this.message = error.response.data.error;
        }
      }
    }
  };
  </script>