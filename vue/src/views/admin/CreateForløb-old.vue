  <template>
    <div>
      <h2>Opret Forløb</h2>
      <form @submit.prevent="submitForm">
        <div>
          <label for="name">Forløb Navn:</label>
          <input type="text" v-model="form.name" required />
        </div>
        <div>
          <label for="startdate">Startdato:</label>
          <input type="date" v-model="form.startdate" required />
        </div>
        <div>
          <label for="enddate">Slutdato:</label>
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
          <label for="emailType">Email Type:</label>
          <select v-model="emailType" @change="clearEmail">
            <option value="randersmail">Randers Email</option>
            <option value="private">Privat Email</option>
          </select>
        </div>
        <div v-if="emailType === 'randersmail'">
          <label for="usermail">Randers Mail:</label>
          <input type="text" v-model="emailSearch" placeholder="Search user emails" />
          <select v-model="form.usermail" required>
            <option v-for="email in filteredEmails" :key="email" :value="email">
              {{ email }}
            </option>
          </select>
        </div>
        <div v-if="emailType === 'private'">
          <label for="privateEmail">Privat Email:</label>
          <input type="email" v-model="form.privateEmail" placeholder="Enter private email" required />
        </div>
        <div>
          <label for="userdq">Medarbejder DQ-Nummer:</label>
          <input type="text" v-model="dqSearch" placeholder="Search user DQ numbers" />
          <select v-model="form.userdq" required>
            <option v-for="dq in filteredDQs" :key="dq" :value="dq">
              {{ dq }}
            </option>
          </select>
        </div>
        <div>
          <label for="ForløbsskabelonID">Forløbsskabelon: (optional)</label>
          <select v-model="form.ForløbsskabelonID">
            <option :value="null">None</option>
            <option v-for="skabelon in forloebsskabeloner" :key="skabelon.ForløbsskabelonID" :value="skabelon.ForløbsskabelonID">
              {{ skabelon.name }}
            </option>
          </select>
        </div>
        <button class="button button-outline" type="submit">Opret Forløb</button>
      </form>
      <div v-if="message">{{ message }}</div>
    </div>
  </template>
  
  <script>
  import { getForloebsskabeloner } from '../../services/forløbsskabelonService';
  import { createForloeb } from '../../services/forløbService';
  import keycloak from '@/keycloak';
  import { getAdminNames, getEmail, getDQ } from '../../services/userService';
  
  export default {
    data() {
      return {
        form: {
          name: '',
          startdate: '',
          enddate: '',
          admin: '',
          usermail: '',
          privateEmail: '',
          userdq: '',
          ForløbsskabelonID: null
        },
        emailType: '',
        forloebsskabeloner: [],
        adminNames: [],
        adminSearch: '',
        emails: [],
        emailSearch: '',
        dqNumbers: [],
        dqSearch: '',
        message: ''
      };
    },
    async created() {
      try {
        const skabelonResponse = await getForloebsskabeloner();
        this.forloebsskabeloner = skabelonResponse.data;
  
        const adminResponse = await getAdminNames();
        this.adminNames = adminResponse.data.admin_names;
  
        const emailResponse = await getEmail();
        this.emails = emailResponse.data.emails;
  
        const dqResponse = await getDQ();
        this.dqNumbers = dqResponse.data.dq_numbers;

        if (keycloak.authenticated) {
          this.form.admin = keycloak.tokenParsed?.name || 'No name';
        }
      } catch (error) {
        this.message = 'Failed to load data';
      }
    },
    computed: {
      filteredAdminNames() {
        return this.adminNames.filter(admin =>
          admin.toLowerCase().includes(this.adminSearch.toLowerCase())
        );
      },
      filteredEmails() {
        return this.emails.filter(email =>
          email.toLowerCase().includes(this.emailSearch.toLowerCase())
        );
      },
      filteredDQs() {
        return this.dqNumbers.filter(dq =>
          dq.toLowerCase().includes(this.dqSearch.toLowerCase())
        );
      }
    },
    methods: {
      clearEmail() {
        this.form.usermail = '';
        this.form.privateEmail = '';
      },
      async submitForm() {
        try {
          const formData = { ...this.form };
          if (!formData.ForløbsskabelonID) {
            delete formData.ForløbsskabelonID;
          }
          if (this.emailType === 'private') {
            formData.usermail = formData.privateEmail;
          }
          delete formData.privateEmail;
          const response = await createForloeb(formData);
          this.message = response.data.message;
        } catch (error) {
          this.message = error.response.data.error;
        }
      }
    }
  };
  </script>