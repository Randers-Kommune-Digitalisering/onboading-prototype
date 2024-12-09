  <template>
    <div>
      <h2>Opret Forløb</h2>
      <form @submit.prevent="submitForm">
        <div>
          <label for="startdate">Start Date:</label>
          <input type="date" v-model="form.startdate" required />
        </div>
        <div>
          <label for="enddate">End Date:</label>
          <input type="date" v-model="form.enddate" required />
        </div>
        <div>
          <label for="admin">Admin:</label>
          <input type="text" v-model="form.admin" required />
        </div>
        <div>
          <label for="usermail">User Mail:</label>
          <input type="email" v-model="form.usermail" required />
        </div>
        <div>
          <label for="userdq">User DQ:</label>
          <input type="text" v-model="form.userdq" required />
        </div>
        <div>
          <label for="ForløbsskabelonID">Forløbsskabelon Name: (optional)</label>
          <select v-model="form.ForløbsskabelonID">
            <option :value="null">None</option>
            <option v-for="skabelon in forloebsskabeloner" :key="skabelon.ForløbsskabelonID" :value="skabelon.ForløbsskabelonID">
              {{ skabelon.name }}
            </option>
          </select>
        </div>
        <button class="button button-outline" type="submit">Create Forløb</button>
      </form>
      <div v-if="message">{{ message }}</div>
    </div>
  </template>
  
  <script>
  import { createForloeb, getForloebsskabeloner } from '../apiService';
  
  export default {
    data() {
      return {
        form: {
          startdate: '',
          enddate: '',
          admin: '',
          usermail: '',
          userdq: '',
          ForløbsskabelonID: null
        },
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
        try {
          const formData = { ...this.form };
          if (!formData.ForløbsskabelonID) {
            delete formData.ForløbsskabelonID;
          }
          const response = await createForloeb(formData);
          this.message = response.data.message;
        } catch (error) {
          this.message = error.response.data.error;
        }
      }
    }
  };
  </script>