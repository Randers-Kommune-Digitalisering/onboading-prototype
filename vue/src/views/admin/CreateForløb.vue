<script setup>
    import { ref, onMounted } from 'vue'
    import { useRouter, useRoute } from 'vue-router'

    import { getUserInfo } from '../../services/keycloakService.js'
    import { getForloebsskabeloner } from '@/services/forløbsskabelonService.js'
    import { createForloeb, getForloebById, updateForloeb } from '@/services/forløbService.js'
    import { getAdminData, getEmail } from '@/services/userService.js'

    const route = useRoute()
    const router = useRouter()

    const isSubmitting = ref(false)
    const isEditing = route.query.edit === 'true'
    const forloeb_id = isEditing ? parseInt(route.query.id, 10) : null

	const template_id = parseInt(route.query.tid, 10)
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
    const isUserMailValid = ref(true)
    const userMailList = ref([])
    const userMailSearchResults = ref([])
    const isUserMailSearchOpen = ref(false)

    const searchUserMails = (searchString) => {
        if (isAdminSearchOpen) {
            isAdminSearchOpen.value = false
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
        inputFields.value.usermail = userMail
        isUserMailSearchOpen.value = false
        evaluateEmail()
    }

    const getEmailType = () => {
        if (inputFields.value.usermail.includes('@randers.dk')) {
            return 'randersmail'
        }
        return 'private'
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
        if (isUserMailSearchOpen) {
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
    
    const selectNoTemplateIfNotSelected = () => {
        if(inputFields.value.ForløbsskabelonID == "")
        {
            inputFields.value.ForløbsskabelonID = null
        }
    }

    const setEndDateFromTemplate = () => {
        const template = templates.value.find(template => template.ForløbsskabelonID === inputFields.value.ForløbsskabelonID)
        if (template) {
            const startDate = new Date(inputFields.value.startdate)
            const daysToAdd = template.varighed
            var endDate = new Date(startDate)
            endDate.setDate(endDate.getDate() + daysToAdd)
            inputFields.value.enddate = endDate.toISOString().split('T')[0]
        }
    }

    /* Instantiate */
    onMounted(async () => {
        try {
            const forloebsskabelonerResponse = await getForloebsskabeloner()
            templates.value = forloebsskabelonerResponse.data
            if (template_id) {
                const selectedTemplate = templates.value.find(template => template.ForløbsskabelonID === template_id)
                if (selectedTemplate)
                    inputFields.value.ForløbsskabelonID = selectedTemplate.ForløbsskabelonID
            }
        } catch (error) {
            console.error('Error fetching forloebsskabeloner:', error)
        }

        try {
            const adminDataResponse = await getAdminData()
            const parsedData = typeof adminDataResponse.data === 'string' ? JSON.parse(adminDataResponse.data) : adminDataResponse.data
            adminList.value = parsedData

            console.log('Logged in admin: ', loggedInAdmin.value)

            // Add admin name to list if not already present
            if (!(parsedData.map(admin => admin.mail)).includes(loggedInAdmin.value)) {
                adminList.value.push({ name: loggedInAdminName.value, mail: loggedInAdmin.value })
            }
        } catch (error) {
            console.error('Error fetching admin names:', error)
        }

        try {
            const emailResponse = await getEmail()
            userMailList.value = emailResponse.data.emails
        } catch (error) {
            console.error('Error fetching emails:', error)
        }

        if (isEditing) {
            try {
                const forloebResponse = await getForloebById(forloeb_id)
                selectedAdmin.value = adminList.value.find(admin => admin.mail === forloebResponse.data.admin)
                const formattedData = {
                    ...forloebResponse.data,
                    startdate: forloebResponse.data.startdate ? forloebResponse.data.startdate.split('T')[0] : '',
                    enddate: forloebResponse.data.enddate ? forloebResponse.data.enddate.split('T')[0] : ''
                }
                formattedData.admin = selectedAdmin.value.name
                Object.assign(inputFields.value, formattedData)
                console.log('Forløb data:', inputFields.value)
            } catch (error) {
                console.error('Error fetching forløb:', error)
            }
        }

        // Uncomment if needed in the future
        // try {
        //     const dqResponse = await getDQ()
        //     dqList.value = dqResponse.data.dq_numbers
        //     console.log('DQs:', dqResponse.data)
        // } catch (error) {
        //     console.error('Error fetching DQs:', error)
        // }
    })

    /* Submit */

    const submitForm = async () =>
    {
        evaluateEmail()
        if (!isUserMailValid.value)
            return
        
        isSubmitting.value = true
        try {
            const formData = { ...inputFields.value }
            formData.admin = selectedAdmin.value.mail
            
            if (!formData.ForløbsskabelonID)
                delete formData.ForløbsskabelonID

            if (getEmailType() === 'private')
            {
                formData.privateEmail = formData.usermail
                delete formData.usermail
            }
            else 
                delete formData.privateEmail

            const response = isEditing ? await updateForloeb(forloeb_id, formData) : await createForloeb(formData)
            if(response.data.uid)
            {
                console.log('Redirecting to:', `/forloeb-overview?id=${response.data.uid}`)
                router.push({ path: '/forloeb-overview', query: { id: response.data.uid } })
            }
        } catch (error) {
            if (error.response?.data?.error) {
                console.log('Error:', error.response.data.error)
            } else {
                console.log('Error:', error)
            }
        }
        isSubmitting.value = false
    }
</script>

<template>
    <p class="indent-tiny bold uppercase p-header-adjust">{{ isEditing ? 'Rediger forløb' : 'Opret forløb' }}</p>

    <form @submit.prevent="submitForm">
    <div class="formContainer">

        <div class="inputContainer">
            <input type="text" id="mail" name="mail" placeholder=" " @input="searchUserMails(inputFields.usermail)" v-model="inputFields.usermail" :class="{'invalid': !isUserMailValid}" required>
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
            
            <div class="itemSelector float-right" v-if="isAdminSearchOpen">
                <span class="float-header small uppercase">Vælg en ansvarlig leder ...</span>
                <div v-for="result in adminSearchResults" @click="selectAdmin(result)">{{result.name}}</div>
                <div v-if="adminSearchResults.length == 0" class="nohover small">Der blev ikke fundet nogle resultater.</div>
            </div>
        </div>

        <div v-if="!isEditing" :class="['inputContainer', { 'hideOnMobile': isUserMailSearchOpen || isAdminSearchOpen }]">
            <select id="template" name="template" v-model="inputFields.ForløbsskabelonID" required>
                <option value="" disabled selected hidden></option>
                <option :value="null">Ingen skabelon</option>
                <option v-for="template in templates" :value="template.ForløbsskabelonID">{{template.name}}</option>
            </select>
            <label for="template" class="floating-label">Skabelon</label>
            <div class="icon nohover"><i class="fa-solid fa-caret-down"></i></div>
        </div>
        
        <div :class="['inputContainer', { 'hideOnMobile': isUserMailSearchOpen || isAdminSearchOpen }]">
            <div class="flex-item">
                <input type="date" id="startdate" name="startdate" v-model="inputFields.startdate" @input="setEndDateFromTemplate()" required>
                <label for="startdate" class="floating-label">Startdato</label>
            </div>
            <div class="flex-item">
                <input type="date" id="enddate" name="enddate" v-model="inputFields.enddate" required>
                <label for="enddate" class="floating-label">Slutdato</label>
            </div>
        </div>

        <div :class="['inputContainer', { 'hideOnMobile': isUserMailSearchOpen || isAdminSearchOpen  }]">
            <input type="text" id="name" name="name" placeholder=" " v-model="inputFields.name" required>
            <label for="name" class="floating-label">Forløbets navn</label>
        </div>

        <div class="inputContainer submit">
            <button :class="['button', 'button-outline', { 'disabled': isSubmitting }, { 'hideOnMobile': isUserMailSearchOpen || isAdminSearchOpen }]" @click="clearAdminIfNotSelected();selectNoTemplateIfNotSelected()" type="submit" :disabled="isSubmitting">{{ isEditing ? 'Opdater forløb' : '+ Opret forløb' }}</button>
        </div>

    </div>
    </form>
</template>