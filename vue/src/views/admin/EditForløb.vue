<script setup>
    import { ref, onMounted } from 'vue'
    import { useRouter, useRoute } from 'vue-router'

    import { getUserInfo } from '@/services/keycloakService.js'
    import { getForloebById, updateForloeb } from '@/services/forløbService.js'
    import { getAdminData, getUsers } from '@/services/userService.js'

    const route = useRoute()
    const router = useRouter()

    const isSubmitting = ref(false)
    const isPreparation = ref(true)
    const forloeb_id = parseInt(route.query.id, 10)

    const inputFields = ref({
        usermail: "",
        admin: "",
        ForløbsskabelonID: "",
        startdate: "",
        enddate: "",
        name: "",
        userdq: ""
    })

    /* User mail search */
    const isUserMailValid = ref(true)
    const isRandersMail = (email) => {
        return email.toLowerCase().endsWith('@randers.dk')
    }
    const welcomeMailPlanned = ref(false)
    const userList = ref([])
    const userMailSearchResults = ref([])
    const isUserMailSearchOpen = ref(false)

    const searchUserMails = (searchString) => {
        if (searchString.includes('@')) {
            let domain = searchString.split('@')[1]
            let domainLength = domain.length
            if (domainLength > 0) {
                let localDomain = ("randers.dk").substring(0, domainLength)
                if(localDomain !== domain) {
                    isUserMailSearchOpen.value = false
                    return
                }
            }
        }
        if (isAdminSearchOpen.value) {
            isAdminSearchOpen.value = false
        }
        if (searchString.length < 3) {
            isUserMailSearchOpen.value = false
            return userMailSearchResults.value = []
        }
        isUserMailSearchOpen.value = true
        searchString = searchString.replace(/Æ/gi, 'a').replace(/Ø/gi, 'o').replace(/Å/gi, 'a')
        let spacelessSearchString = searchString.replace(/ /g, '.')
        const searchResults = userList.value.filter(userMail =>
            userMail.email.toLowerCase().startsWith(searchString.toLowerCase()) ||
            userMail.email.toLowerCase().startsWith(spacelessSearchString.toLowerCase())
        )
        return userMailSearchResults.value = searchResults
    }

    const selectUserMail = (user) => {
        inputFields.value.usermail = user.email
        inputFields.value.userdq = user.dq
        inputFields.value.name = user.name
        isUserMailSearchOpen.value = false
        evaluateEmail()
    }

    const evaluateEmail = () => {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailPattern.test(inputFields.value.usermail))
            return isUserMailValid.value = false
        return isUserMailValid.value = true
    }

    /* Admin search */
    const loggedInAdmin = ref('')
    const loggedInAdminName = ref('')
    const isAdminLocked = ref(true)
    const adminList = ref([])
    const adminSearchResults = ref([])
    const isAdminSearchOpen = ref(false)
    const selectedAdmin = ref(null)

    getUserInfo().then(userInfo => {
        loggedInAdmin.value = userInfo.email || 'No mail'
        loggedInAdminName.value = userInfo.name || 'No name'
        selectAdmin({name: loggedInAdminName.value, mail: loggedInAdmin.value})
    })

    const searchAdmins = (searchString) => {
        if (isUserMailSearchOpen.value) {
            isUserMailSearchOpen.value = false
        }
        if (searchString.length < 3) {
            isAdminSearchOpen.value = false
            return adminSearchResults.value = []
        }
        isAdminSearchOpen.value = true
        return adminSearchResults.value = adminList.value
            .filter(admin => admin.name.toLowerCase().includes(searchString.toLowerCase()))
            .slice(0, 8)
    }

    const selectAdmin = (admin) => {
        selectedAdmin.value = admin
        inputFields.value.admin = admin.name
        isAdminLocked.value = true
        isAdminSearchOpen.value = false
    }

    const toggleadminSearch = () => {
        if(adminList.value.map(admin => admin.name).includes(inputFields.value.admin))
        {
            isAdminLocked.value = !isAdminLocked.value
            isAdminSearchOpen.value = false
        }
        else
            isAdminLocked.value = false
    }

    const clearAdminIfNotSelected = () => {
        if(!adminList.value.map(admin => admin.name).includes(inputFields.value.admin))
        {
            inputFields.value.admin = ""
            isAdminLocked.value = false
            isAdminSearchOpen.value = false
        }
    }

    /* Instantiate */
    onMounted(async () => {
        // Get admin list
        try {
            const adminDataResponse = await getAdminData()
            const parsedData = typeof adminDataResponse.data === 'string' ? JSON.parse(adminDataResponse.data) : adminDataResponse.data
            adminList.value = parsedData

            // Add admin name to list if not already present
            if (!(parsedData.map(admin => admin.mail)).includes(loggedInAdmin.value)) {
                adminList.value.push({ name: loggedInAdminName.value, mail: loggedInAdmin.value })
            }
        } catch (error) {
            console.error('Error fetching admin names:', error)
        }

        // Get user list
        try {
            const userResponse = await getUsers()
            userList.value = userResponse.data
        } catch (error) {
            console.error('Error fetching emails:', error)
        }

        // Get item to edit
        try {
            const forloebResponse = await getForloebById(forloeb_id)
            selectedAdmin.value = adminList.value.find(admin => admin.mail === forloebResponse.data.admin)
            const formattedData = {
                ...forloebResponse.data,
                startdate: forloebResponse.data.startdate ? forloebResponse.data.startdate.split('T')[0] : '',
                enddate: forloebResponse.data.enddate ? forloebResponse.data.enddate.split('T')[0] : ''
            }
            formattedData.admin = selectedAdmin.value.name
            isPreparation.value = forloebResponse.data.isPreparation
            Object.assign(inputFields.value, formattedData)
        } catch (error) {
            console.error('Error fetching forløb:', error)
        }
    })

    /* Submit */

    const submitForm = async () => {
        evaluateEmail()
        if (!isUserMailValid.value)
            return
        isSubmitting.value = true
        try {
            const formData = { ...inputFields.value }
            formData.admin = selectedAdmin.value.mail
            if (!formData.ForløbsskabelonID)
                delete formData.ForløbsskabelonID
            const response = await updateForloeb(forloeb_id, formData)
            if (response.data.uid)
                router.push({ path: '/forloeb-overview', query: { id: response.data.uid } })
        } catch (error) {
            if (error.response?.data?.error)
                console.error('Error:', error.response.data?.error)
            else
                console.error('Error:', error)
        }
        isSubmitting.value = false
    }
</script>

<template>
    <p class="indent-tiny bold uppercase p-header-adjust">Rediger forløb</p>

    <form @submit.prevent="submitForm">
    <div class="formContainer">

        <div class="inputContainer">
            <input type="text" id="mail" name="mail" placeholder=" " @input="searchUserMails(inputFields.usermail)" v-model="inputFields.usermail" :class="{'invalid': !isUserMailValid}" required>
            <label for="mail" class="floating-label">Medarbejder mailadresse</label>

            <div class="itemSelector float-right" v-if="isUserMailSearchOpen">
                <span class="float-header small uppercase">Vælg en mailadresse ...</span>
                <div v-for="result in userMailSearchResults" @click="selectUserMail(result)" class="small">{{result.email}}</div>
                <div v-if="userMailSearchResults.length == 0" class="nohover small">Der blev ikke fundet nogle resultater.</div>
            </div>
        </div>

        <div :class="['inputContainer', { 'hideOnMobile': isUserMailSearchOpen || isAdminSearchOpen  }]">
            <input type="text" id="name" name="name" placeholder=" " v-model="inputFields.name" required>
            <label for="name" class="floating-label">Medarbejder navn</label>
        </div>

        <div :class="['inputContainer', { 'hideOnMobile': isUserMailSearchOpen }]">
            <input type="text" id="admin" name="admin" placeholder=" " @input="searchAdmins(inputFields.admin)" v-model="inputFields.admin" class="locked" required :disabled="isAdminLocked">
            <label for="admin" class="floating-label">Ansvarlig leder</label>
            <div class="icon" @click="toggleadminSearch()"><i :class="'fa-solid fa-lock' + (isAdminLocked ? '' : '-open')"></i></div>
            
            <div class="itemSelector float-right" v-if="isAdminSearchOpen">
                <span class="float-header small uppercase">Vælg en ansvarlig leder ...</span>
                <div v-for="result in adminSearchResults" @click="selectAdmin(result)">{{result.name}}</div>
                <div v-if="adminSearchResults.length == 0" class="nohover small">Der blev ikke fundet nogle resultater.</div>
            </div>
        </div>
        <div v-if="!isPreparation" class="inputContainer" :class="{ 'hideOnMobile': isUserMailSearchOpen || isAdminSearchOpen }">
            <div class="flex-item">
                <input type="date" id="startdate" name="startdate" v-model="inputFields.startdate" required>
                <label for="startdate" class="floating-label">Startdato</label>
            </div>
            <div class="flex-item">
                <input type="date" id="enddate" name="enddate" v-model="inputFields.enddate" required>
                <label for="enddate" class="floating-label">Slutdato</label>
            </div>
        </div>

        <div class="inputContainer submit">
            <button :class="['button', { 'disabled': isSubmitting }, { 'hideOnMobile': isUserMailSearchOpen || isAdminSearchOpen }]" @click="clearAdminIfNotSelected()" type="submit" :disabled="isSubmitting">Opdater forløb</button>
        </div>

    </div>
    </form>
</template>