<script setup>
    import { ref, onMounted } from 'vue'
    import { useRouter, useRoute } from 'vue-router'
    
    import { getForloebById, startForloeb } from '@/services/forløbService.js'
    import { getUsers } from '@/services/userService.js'

    const route = useRoute()
    const router = useRouter()

    const isSubmitting = ref(false)
    const forloeb_id = parseInt(route.query.id, 10)

    const inputFields = ref({
        usermail: "",
        startdate: "",
        enddate: "",
        planMails: true
    })

    /* User mail search */
    const isUserMailValid = ref(true)
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
    
    const setEndDateFromSelf = () => {
        const startDate = new Date(inputFields.value.startdate)
        const daysToAdd = inputFields.value.varighed
        var endDate = new Date(startDate)
        endDate.setDate(endDate.getDate() + daysToAdd)
        inputFields.value.enddate = endDate.toISOString().split('T')[0]
    }

    /* Instantiate */
    onMounted(async () => {
        if (!forloeb_id) {
            router.replace('/admin-overview')
            return
        }
        // Get user list
        try {
            const userResponse = await getUsers()
            userList.value = userResponse.data
        } catch (error) {
            console.error('Error fetching emails:', error)
        }

        // Get forløb to start
        try {
            const forloebResponse = await getForloebById(forloeb_id)
            if(forloebResponse.data?.isPreparation === false || forloebResponse.data?.error) {
                console.error('Error fetching forløb or forløb not in preparation:', forloebResponse.data.error)
                router.replace('/admin-overview')
                return
            }
            Object.assign(inputFields.value, forloebResponse.data)
        } catch (error) {
            console.error('Error fetching forløb:', error)
        }
    })

    /* Submit */

    const submitForm = async () =>
    {
        evaluateEmail()
        if (!isUserMailValid.value)
            return
        
        isSubmitting.value = true
        try {
            const formData = {
                ForløbID: forloeb_id,
                startdate: inputFields.value.startdate,
                enddate: inputFields.value.enddate,
                planMails: inputFields.value.planMails
            }
            const response = await startForloeb(formData)
            if(response.data?.uid)
                router.push({ path: '/forloeb-overview', query: { id: response.data.uid } })
            
        } catch (error) {
            if (error.response?.data?.error)
                console.error('Error:', error.response.data.error)
            else 
                console.error('Error:', error)
        }
        isSubmitting.value = false
    }
</script>

<template>
    <p class="indent-tiny bold uppercase p-header-adjust">Start forløb</p>

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

        <div :class="['inputContainer', { 'hideOnMobile': isUserMailSearchOpen }]">
            <input type="text" id="name" name="name" placeholder=" " v-model="inputFields.name" required>
            <label for="name" class="floating-label">Medarbejder navn</label>
        </div>

        <div :class="['inputContainer', { 'hideOnMobile': isUserMailSearchOpen }]">
            <div class="flex-item">
                <input type="date" id="startdate" name="startdate" v-model="inputFields.startdate" @input="setEndDateFromSelf()" required>
                <label for="startdate" class="floating-label">Startdato</label>
            </div>
            <div class="flex-item">
                <input type="date" id="enddate" name="enddate" v-model="inputFields.enddate" required>
                <label for="enddate" class="floating-label">Slutdato</label>
            </div>
        </div>

        <div :class="['inputContainer checkbox', { 'hideOnMobile': isUserMailSearchOpen }]">
            <input type="checkbox" id="planMails" name="planMails" v-model="inputFields.planMails">
            <label for="planMails" class="checkbox-label">Planlæg afsendelse af mails til opgaveansvarlige</label>
        </div>

        <div class="inputContainer submit">
            <button :class="['button', 'button-outline', { 'disabled': isSubmitting }, { 'hideOnMobile': isUserMailSearchOpen }]" type="submit" :disabled="isSubmitting">Start forløb</button>
        </div>

    </div>
    </form>
</template>