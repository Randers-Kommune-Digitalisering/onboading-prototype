<script setup>
    import { ref } from 'vue'

    const inputFields = ref({
        userMail: "",
        admin: "",
        department: "",
        startDate: "",
        endDate: "",
        courseName: ""
    })

    /* User mail search */
    const demoUserMailList = ref(["test@randers.dk", "soren.langbo.sloto.thomassen@randers.dk"])
    const demoUserMailSearchResults = ref([])
    const isUserMailSearchOpen = ref(false)

    const searchUserMails = (searchString) => {
        if (isAdminSearchOpen) {
            isAdminSearchOpen.value = false
        }
        if (searchString.length < 3) {
            isUserMailSearchOpen.value = false
            return demoUserMailSearchResults.value = []
        }
        isUserMailSearchOpen.value = true
        searchString = searchString.replace(/Æ/gi, 'a').replace(/Ø/gi, 'o').replace(/Å/gi, 'a')
        let spacelessSearchString = searchString.replace(/ /g, '.')
        const searchResults = demoUserMailList.value.filter(userMail =>
            userMail.toLowerCase().startsWith(searchString.toLowerCase()) ||
            userMail.toLowerCase().startsWith(spacelessSearchString.toLowerCase())
        )
        return demoUserMailSearchResults.value = searchResults
    }

    const selectUserMail = (userMail) => {
        inputFields.value.userMail = userMail
        isUserMailSearchOpen.value = false
    }

    /* Admin search */
    const isAdminLocked = ref(true)
    const demonAdminList = ref(["Jens Jensen", "Thomas Thomassen"])
    const demoAdminSearchResults = ref([])
    const isAdminSearchOpen = ref(false)

    const searchAdmins = (searchString) => {
        if (isUserMailSearchOpen) {
            isUserMailSearchOpen.value = false
        }
        if (searchString.length < 3) {
            isAdminSearchOpen.value = false
            return demoAdminSearchResults.value = []
        }
        isAdminSearchOpen.value = true
        return demoAdminSearchResults.value = demonAdminList.value.filter(admin =>
            admin.toLowerCase().includes(searchString.toLowerCase())
        )
    }

    const selectAdmin = (admin) => {
        inputFields.value.admin = admin
        isAdminLocked.value = true
        isAdminSearchOpen.value = false
    }

    const toggleAdminSearch = () => {
        if(demonAdminList.value.includes(inputFields.value.admin))
        {
            isAdminLocked.value = !isAdminLocked.value
            isAdminSearchOpen.value = false
        }
        else
            isAdminLocked.value = false
    }

</script>

<template>
    <p class="indent-tiny bold uppercase p-header-adjust">Opret forløb</p>

    <form @submit.prevent="submitForm">
    <div class="formContainer">

        <div class="inputContainer">
            <input type="text" id="name" name="name" placeholder=" " @input="searchUserMails(inputFields.userMail)" v-model="inputFields.userMail" required>
            <label for="name" class="floating-label">Medarbejder mailadresse</label>

            <div class="itemSelector float-right" v-if="isUserMailSearchOpen">
                <span class="float-header small uppercase">Vælg en mailadresse ...</span>
                <div v-for="result in demoUserMailSearchResults" @click="selectUserMail(result)" class="small">{{result}}</div>
                <div v-if="demoUserMailSearchResults.length == 0" class="nohover small">Der blev ikke fundet nogle resultater.</div>
            </div>
        </div>

        <div :class="['inputContainer', { 'hideOnMobile': isUserMailSearchOpen }]">
            <input type="text" id="admin" name="admin" placeholder=" " @input="searchAdmins(inputFields.admin)" v-model="inputFields.admin" class="locked" required :disabled="isAdminLocked">
            <label for="admin" class="floating-label">Ansvarlig leder</label>
            <div class="icon" @click="toggleAdminSearch()"><i :class="'fa-solid fa-lock' + (isAdminLocked ? '' : '-open')"></i></div>
            
            <div class="itemSelector float-right" v-if="isAdminSearchOpen">
                <span class="float-header small uppercase">Vælg en ansvarlig leder ...</span>
                <div v-for="result in demoAdminSearchResults" @click="selectAdmin(result)">{{result}}</div>
                <div v-if="demoAdminSearchResults.length == 0" class="nohover small">Der blev ikke fundet nogle resultater.</div>
            </div>
        </div>

        <div :class="['inputContainer', { 'hideOnMobile': isUserMailSearchOpen || isAdminSearchOpen }]">
            <select id="department" name="department" v-model="inputFields.department" required>
                <option value="" disabled selected hidden></option>
                <option value="HR">HR</option>
                <option value="IT">IT</option>
                <option value="Finance">Finance</option>
                <option value="Marketing">Marketing</option>
            </select>
            <label for="department" class="floating-label">Afdeling</label>
            <div class="icon nohover"><i class="fa-solid fa-caret-down"></i></div>
        </div>
        
        <div :class="['inputContainer', { 'hideOnMobile': isUserMailSearchOpen || isAdminSearchOpen }]">
            <div class="flex-item">
                <input type="date" id="startDate" name="startDate" v-model="inputFields.startDate" required>
                <label for="startDate" class="floating-label">Startdato</label>
            </div>
            <div class="flex-item">
                <input type="date" id="endDate" name="endDate" v-model="inputFields.endDate" required>
                <label for="endDate" class="floating-label">Slutdato</label>
            </div>
        </div>

        <div :class="['inputContainer', { 'hideOnMobile': isUserMailSearchOpen || isAdminSearchOpen  }]">
            <input type="text" id="name" name="name" placeholder=" " v-model="inputFields.courseName" required>
            <label for="name" class="floating-label">Forløbets navn</label>

        </div>

        <div class="inputContainer submit">
            <button class="button button-outline" type="submit">Opret forløb</button>
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