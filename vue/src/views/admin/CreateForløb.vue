<script setup>
    import { ref, onMounted } from 'vue'

    import { getForloebsskabeloner } from '../../services/forløbsskabelonService';
    import { createForloeb } from '../../services/forløbService';
    import keycloak from '@/keycloak';
    import { getAdminNames, getEmail, getDQ } from '../../services/userService';

    const templates = ref([])
    const inputFields = ref({
        usermail: "",
        admin: "",
        ForløbsskabelonID: "",
        startdate: "",
        enddate: "",
        name: "",
        privateEmail: '',
        userdq: ''
    })

    // const dqList = ref([])

    /* User mail search */
    const userMailList = ref([])
    const userMailSearchResults = ref([])
    const isUserMailSearchOpen = ref(false)

    const searchUserMails = (searchString) => {
        if (isadminSearchOpen) {
            isadminSearchOpen.value = false
        }
        if (searchString.length < 3) {
            isUserMailSearchOpen.value = false
            return userMailSearchResults.value = []
        }
        isUserMailSearchOpen.value = true
        searchString = searchString.replace(/Æ/gi, 'a').replace(/Ø/gi, 'o').replace(/Å/gi, 'a')
        let spacelessSearchString = searchString.replace(/ /g, '.')
        const searchResults = userMailList.value.filter(userMail =>
            userMail.toLowerCase().startsWith(searchString.toLowerCase()) ||
            userMail.toLowerCase().startsWith(spacelessSearchString.toLowerCase())
        )
        return userMailSearchResults.value = searchResults
    }

    const selectUserMail = (userMail) => {
        inputFields.value.userMail = userMail
        isUserMailSearchOpen.value = false
    }

    const getEmailType = () => {
        if (inputFields.value.usermail.includes('@randers.dk')) {
            return 'randersmail'
        }
        return 'private'
    }

    /* Admin search */
    const isAdminLocked = ref(true)
    const adminList = ref([])
    const adminSearchResults = ref([])
    const isadminSearchOpen = ref(false)

    const searchAdmins = (searchString) => {
        if (isUserMailSearchOpen) {
            isUserMailSearchOpen.value = false
        }
        if (searchString.length < 3) {
            isadminSearchOpen.value = false
            return adminSearchResults.value = []
        }
        isadminSearchOpen.value = true
        return adminSearchResults.value = adminList.value
            .filter(admin => admin.toLowerCase().includes(searchString.toLowerCase()))
            .slice(0, 8)
    }

    const selectAdmin = (admin) => {
        inputFields.value.admin = admin
        isAdminLocked.value = true
        isadminSearchOpen.value = false
    }

    const toggleadminSearch = () => {
        if(adminList.value.includes(inputFields.value.admin))
        {
            isAdminLocked.value = !isAdminLocked.value
            isadminSearchOpen.value = false
        }
        else
            isAdminLocked.value = false
    }

    const clearAdminIfNotSelected = () => {
        if(!adminList.value.includes(inputFields.value.admin))
        {
            inputFields.value.admin = ""
            isAdminLocked.value = false
            isadminSearchOpen.value = false
        }
    }

    /* Instantiate */
    onMounted(() => {
        getForloebsskabeloner().then(data => {
            templates.value = data.data
        }).catch(error => {
            console.error('Error fetching forloebsskabeloner:', error)
        })

        getAdminNames().then(data => {
            adminList.value = data.data.admin_names
        }).catch(error => {
            console.error('Error fetching admin names:', error)
        })

        getEmail().then(data => {
            userMailList.value = data.data.emails
        }).catch(error => {
            console.error('Error fetching emails:', error)
        })

        // getDQ().then(data => {
        //     dqList.value = data.data.dq_numbers
        //     console.log('DQs:', data.data)
        // }).catch(error => {
        //     console.error('Error fetching DQs:', error)
        // })
    })

    /* Submit */

    const submitForm = async () =>
    {
        try {
            const formData = { ...inputFields.value }
            if (!formData.ForløbsskabelonID)
                delete formData.ForløbsskabelonID

            if (getEmailType() === 'private')
            {
                formData.privateEmail = formData.usermail
                delete formData.usermail
            }
            else 
                delete formData.privateEmail

            const response = await createForloeb(formData)
            console.log('Response:', response.data.message)
        } catch (error) {
            console.log('Error:', response.data.error)
        }
}

</script>

<template>
    <p class="indent-tiny bold uppercase p-header-adjust">Opret forløb</p>

    <form @submit.prevent="submitForm">
    <div class="formContainer">

        <div class="inputContainer">
            <input type="text" id="mail" name="mail" placeholder=" " @input="searchUserMails(inputFields.usermail)" v-model="inputFields.usermail" required>
            <label for="mail" class="floating-label">Medarbejder mailadresse</label>

            <div class="itemSelector float-right" v-if="isUserMailSearchOpen">
                <span class="float-header small uppercase">Vælg en mailadresse ...</span>
                <div v-for="result in userMailSearchResults" @click="selectUserMail(result)" class="small">{{result}}</div>
                <div v-if="userMailSearchResults.length == 0" class="nohover small">Der blev ikke fundet nogle resultater.</div>
            </div>
        </div>

        <div :class="['inputContainer', { 'hideOnMobile': isUserMailSearchOpen }]">
            <input type="text" id="admin" name="admin" placeholder=" " @input="searchAdmins(inputFields.admin)" v-model="inputFields.admin" class="locked" required :disabled="isAdminLocked">
            <label for="admin" class="floating-label">Ansvarlig leder</label>
            <div class="icon" @click="toggleadminSearch()"><i :class="'fa-solid fa-lock' + (isAdminLocked ? '' : '-open')"></i></div>
            
            <div class="itemSelector float-right" v-if="isadminSearchOpen">
                <span class="float-header small uppercase">Vælg en ansvarlig leder ...</span>
                <div v-for="result in adminSearchResults" @click="selectAdmin(result)">{{result}}</div>
                <div v-if="adminSearchResults.length == 0" class="nohover small">Der blev ikke fundet nogle resultater.</div>
            </div>
        </div>

        <div :class="['inputContainer', { 'hideOnMobile': isUserMailSearchOpen || isadminSearchOpen }]">
            <select id="template" name="template" v-model="inputFields.ForløbsskabelonID">
                <option :value="null" disabled selected hidden></option>
                <option v-for="template in templates" :value="template.ForløbsskabelonID">{{template.name}}</option>
                <option v-if="templates.length == 0" disabled>Ingen skabeloner</option>
            </select>
            <label for="template" class="floating-label">Skabelon</label>
            <div class="icon nohover"><i class="fa-solid fa-caret-down"></i></div>
        </div>
        
        <div :class="['inputContainer', { 'hideOnMobile': isUserMailSearchOpen || isadminSearchOpen }]">
            <div class="flex-item">
                <input type="date" id="startdate" name="startdate" v-model="inputFields.startdate" required>
                <label for="startdate" class="floating-label">Startdato</label>
            </div>
            <div class="flex-item">
                <input type="date" id="enddate" name="enddate" v-model="inputFields.enddate" required>
                <label for="enddate" class="floating-label">Slutdato</label>
            </div>
        </div>

        <div :class="['inputContainer', { 'hideOnMobile': isUserMailSearchOpen || isadminSearchOpen  }]">
            <input type="text" id="name" name="name" placeholder=" " v-model="inputFields.courseName" required>
            <label for="name" class="floating-label">Forløbets navn</label>

        </div>

        <div class="inputContainer submit">
            <button class="button button-outline" @click="clearAdminIfNotSelected()" type="submit">Opret forløb</button>
        </div>

    </div>
    </form>
</template>

<style scoped>
    .formContainer {
        position: relative;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .inputContainer {
        position: relative;
        display: flex;
        flex-direction: row;
        gap: 1rem;
    }
    .inputContainer > .flex-item {
        flex-grow: 1;
        position: relative;
    }
    .inputContainer.submit {
        display: flex;
        flex-direction: row;
        justify-content: flex-end;
    }

    .float-right {
        position: absolute;
        margin-top: 5rem; /*4.16rem;*/
        z-index: 10;
        width: 100%;
    }
    @media only screen and (min-width: 768px) {
        .float-right {
            margin-top: 0rem;
            position: absolute;
            margin-left: calc(100% + 1.5rem);
            max-width: 18rem;
        }
    }
    .itemSelector {
        display: block;

        background-color: rgb(230, 224, 216);
        border-radius: 0.2rem;
    }
    .itemSelector div {
        padding-left: 1rem;
        padding-right: 1rem;
        line-height: 3.15rem;

        overflow: hidden;
        text-overflow: ellipsis;
    }
    .itemSelector div:first-of-type {
        border-top-left-radius: 0.2rem;
        border-top-right-radius: 0.2rem;
    }
    .itemSelector div:last-of-type {
        border-bottom-left-radius: 0.2rem;
        border-bottom-right-radius: 0.2rem;
    }
    .itemSelector div:not(.nohover):hover {
        background-color: rgb(241, 237, 232);
        cursor: pointer;
    }
    .float-header {
        position: absolute;
        transform: translateY(calc(-100% - 0.5rem));
        padding-left: 0.5rem;
    }

    .floating-label {
        position: absolute;
        top: 0.9rem;
        left: 0.8rem;
        pointer-events: none;
        transition: 0.2s ease all;
        color: #787878;
        font-size: 1em;
    }
    input[type=text], input[type=date], select {
        background-color: rgb(241, 237, 232);
        width: 100%;
        padding: 1.6rem 0.8rem 0.6rem 0.8rem;
        box-sizing: border-box;
        border-radius: 0.2rem;
        border: 0rem;
        transition-duration: 200ms;
    }
    select {
        appearance: none;
    }
    input[type=text]:focus, input[type=date]:focus, select:focus {
        outline:none;
        background-color: rgb(248, 246, 244);
    }
    input:disabled {
        background-color: rgb(230, 224, 216);
        color: #4b8049;
        font-weight: 600;
    }
    .icon {
        position: absolute;
        right: 0rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 0.2rem;
        padding: 1.1rem;
        height: 100%;
        transition: 150ms;
    }
    .icon:hover:not(.nohover) {
        color: #4b8049;
        cursor: pointer;
    }
    .icon.nohover {
        pointer-events: none;
    }
    @media only screen and (min-width: 768px) {
        .floating-label {
        top: 0.9rem;
        left: 0.8rem;
        }
        .inputContainer  {
        width: 30rem;
        }
        .icon {
        right: auto;
        left: 27rem;
        }
    }

    input[type=text]:focus + .floating-label,
    input[type=text]:not(:placeholder-shown) + .floating-label,
    input[type=date] + .floating-label, /* :valid for date, if selection is required */
    select:valid + .floating-label {
        top: 0.5rem;
        left: 0.8rem;
        color: #8b8b8b;
        font-size: 0.8em;
    }

    @media only screen and (max-width: 768px) {
        .hideOnMobile {
            opacity: 0;
            overflow: hidden;
            pointer-events: none;
        }
    }
</style>