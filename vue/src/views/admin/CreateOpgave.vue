<script setup>
    import { ref, onMounted } from 'vue'
    import { useRoute, useRouter } from 'vue-router'

    import { getAnvarligNames } from '@/services/userService'
    import { createOpgave } from '@/services/opgaveService'
    import { createOpgaveskabelon } from '@/services/opgaveSkabelonService'
    import { getForloebById } from '@/services/forløbService'
    import { getForloebsskabeloner } from '@/services/forløbsskabelonService'

    const route = useRoute()
    const router = useRouter()

    const forloeb = ref(null)
    const forloeb_id = parseInt(route.query.id ?? route.query.tid, 10)
    const addToTemplate = route.query.id == null // Whether we are adding an opgave to a forløbsskabelon
    const isTemplate = false  // Whether we are adding an opgave to a forløb/forløbsskablon or creating a template
    const isSubmitting = ref(false)

    const inputFields = ref({
        title: "",
        ansvarlig: "",
        beskrivelse: "",
        startdato: "",
        slutdato: "",
        result: false,
        timestamp: ""
    })

    /* Assistant search */

    const isAssistantLocked = ref(false)
    const assistantList = ref([])
    const assistantSearchResults = ref([])
    const isAssistantSearchOpen = ref(false)

    const searchAssistants = (searchString) => {
        if (searchString.length < 3) {
            isAssistantSearchOpen.value = false
            return assistantSearchResults.value = []
        }
        isAssistantSearchOpen.value = true
        return assistantSearchResults.value = assistantList.value
            .filter(assistant => assistant.toLowerCase().includes(searchString.toLowerCase()))
            .slice(0, 8)
    }

    const selectAssistant = (assistant) => {
        inputFields.value.ansvarlig = assistant
        isAssistantLocked.value = true
        isAssistantSearchOpen.value = false
    }

    const toggleassistantSearch = () => {
        if(assistantList.value.includes(inputFields.value.ansvarlig))
        {
            isAssistantLocked.value = !isAssistantLocked.value
            isAssistantSearchOpen.value = false
        }
        else
            isAssistantLocked.value = false
    }

    const clearAssistantIfNotSelected = () => {
        if(!assistantList.value.includes(inputFields.value.ansvarlig))
        {
            inputFields.value.ansvarlig = ""
            isAssistantLocked.value = false
            isAssistantSearchOpen.value = false
        }
    }

    /* Textarea */

    const textarea = ref(null)

    const resizeTextareToFitContent = () => {
        // const lineHeight = parseFloat(getComputedStyle(textarea.value).lineHeight)
        // const lines = textarea.value.value.split('\n').length
        textarea.value.style.height = 'auto'
        textarea.value.style.height = (textarea.value.scrollHeight) + 'px'
    }

    /* Instantiate */

    onMounted(() => {
        if(!forloeb_id) {
            console.error('No ID provided')
            router.back()
            return
        }

        if(!isTemplate && !addToTemplate)
            getAnvarligNames().then(response => {
                assistantList.value = response.data.fullnames
            }).catch(error => {
                console.error('Error fetching assistant names:', error)
            })

        if(addToTemplate) // In case we are adding an opgave to a forløbsskabelon
            getForloebsskabeloner().then(response => {
                forloeb.value = response.data.filter(skabelon => skabelon.ForløbsskabelonID == forloeb_id)[0]
                //console.log('Forløbsskabelon:', forloeb.value)
            }).catch(error => {
                console.error('Error fetching forløbsskabelon:', error)
            })
        else
            getForloebById(forloeb_id).then(response => {
                forloeb.value = response.data
                //console.log('Forløb:', forloeb.value)
            }).catch(error => {
                console.error('Error fetching forløb:', error)
            })
    })

    /* Submit */

    const submitForm = async () =>
    {     
        isSubmitting.value = true
        try {
            inputFields.value.timestamp = new Date().toISOString()
            if(addToTemplate)
                inputFields.value.ForløbsskabelonID = forloeb_id
            else
                inputFields.value.ForløbID = forloeb_id

            const formData = { ...inputFields.value }

            const response = isTemplate ? await createOpgaveskabelon(formData) : await createOpgave(formData)
            if(response !== null)
            {
                if (router.getRoutes()[router.getRoutes().length-1].name == "ForløbOverview")
                    router.back()
                else
                    router.replace({ path: '/forloeb-overview', query: { id: forloeb_id } })
            }
            else
                console.log('Response:', response)

        } catch (error) {            
            console.log('Error:', error.response?.data?.error ?? error)
        }
        isSubmitting.value = false
    }
</script>

<template>
    <p class="indent-tiny bold uppercase p-header-adjust">Tilføj opgave til {{ forloeb?.name == '' ? 'forløbet' : forloeb?.name  }}</p>

    <form @submit.prevent="submitForm">
    <div class="formContainer">

        <div class="inputContainer">
            <input type="text" id="title" name="title" placeholder=" " v-model="inputFields.title" required>
            <label for="title" class="floating-label">Opgavens navn</label>
        </div>
        
        <div class="inputContainer" v-if="!isTemplate && !addToTemplate">
            <input type="text" id="assistant" name="assistant" placeholder=" " @input="searchAssistants(inputFields.ansvarlig)" v-model="inputFields.ansvarlig" class="locked" :disabled="isAssistantLocked">
            <label for="assistant" class="floating-label">Ansvarlig medarbejder</label>
            <div class="icon" @click="toggleassistantSearch()"><i :class="'fa-solid fa-lock' + (isAssistantLocked ? '' : '-open')"></i></div>
            
            <div class="itemSelector float-right" v-if="isAssistantSearchOpen">
                <span class="float-header small uppercase">Vælg en ansvarlig medarbejder ...</span>
                <div v-for="result in assistantSearchResults" @click="selectAssistant(result)">{{result}}</div>
                <div v-if="assistantSearchResults.length == 0" class="nohover small">Der blev ikke fundet nogle resultater.</div>
            </div>
        </div>

        <div :class="['inputContainer', { 'hideOnMobile': isAssistantSearchOpen }]">
            <textarea id="description" name="description" ref="textarea" @input="resizeTextareToFitContent()" placeholder=" " v-model="inputFields.beskrivelse" required></textarea>
            <label for="description" class="floating-label">Beskrivelse</label>
        </div>

        <div :class="['inputContainer', { 'hideOnMobile': isAssistantSearchOpen }]" v-if="!isTemplate">
            <div class="flex-item">
                <input type="date" id="startdate" name="startdate" v-model="inputFields.startdato" required>
                <label for="startdate" class="floating-label">Startdato</label>
            </div>
            <div class="flex-item">
                <input type="date" id="enddate" name="enddate" v-model="inputFields.slutdato" required>
                <label for="enddate" class="floating-label">Slutdato</label>
            </div>
        </div>

        <div :class="['inputContainer', { 'hideOnMobile': isAssistantSearchOpen }]" v-if="isTemplate">
            <div class="flex-item">
                <input type="text" id="startdate" name="startdate" v-model="inputFields.startdato" required>
                <label for="startdate" class="floating-label">Startdag (relativ fra forløbets start)</label>
            </div>
            <div class="flex-item">
                <input type="text" id="enddate" name="enddate" v-model="inputFields.slutdato" required>
                <label for="enddate" class="floating-label">Varighed</label>
            </div>
        </div>

        <div :class="['inputContainer', 'submit', { 'hideOnMobile': isAssistantSearchOpen }]">
            <button :class="['button', 'button-outline', { 'disabled': isSubmitting }]" type="submit" @click="clearAssistantIfNotSelected()" :disabled="isSubmitting">+ Tilføj opgave</button>
        </div>

    </div>
    </form>
</template>