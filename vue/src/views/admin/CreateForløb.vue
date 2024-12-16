  <template>
    <div>
      <h2>Opret Forløb</h2>
      <form @submit.prevent="submitForm">
        <div>
          <label for="name">Name:</label>
          <input type="text" v-model="form.name" required />
        </div>
        <div>
          <label for="startdate">Start Date:</label>
          <input type="date" v-model="form.startdate" required />
        </div>
        <div>
          <label for="enddate">End Date:</label>
          <input type="date" v-model="form.enddate" required />
        </div>
        <div>
          <label for="admin">Leder:</label>
          <input type="text" v-model="adminSearch" placeholder="Search admin names" />
          <select v-model="form.admin" required>
            <option v-for="admin in filteredAdminNames" :key="admin" :value="admin">
              {{ admin }}
            </option>
          </select>
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
  import { getForloebsskabeloner } from '../../services/forløbsskabelonService';
  import { createForloeb, getAdminNames } from '../../services/forløbService';
  
  export default {
    data() {
      return {
        form: {
          name: '',
          startdate: '',
          enddate: '',
          admin: '',
          usermail: '',
          userdq: '',
          ForløbsskabelonID: null
        },
        forloebsskabeloner: [],
        adminNames: [],
        adminSearch: '',
        message: ''
      };
    },
    async created() {
      try {
        const skabelonResponse = await getForloebsskabeloner();
        this.forloebsskabeloner = skabelonResponse.data;
  
        const adminResponse = await getAdminNames();
        this.adminNames = adminResponse.data.admin_names;
      } catch (error) {
        this.message = 'Failed to load admin name data';
      }
    },
    computed: {
      filteredAdminNames() {
        return this.adminNames.filter(admin =>
          admin.toLowerCase().includes(this.adminSearch.toLowerCase())
        );
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