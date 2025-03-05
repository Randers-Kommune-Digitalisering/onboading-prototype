<script setup>
    import { ref, onMounted } from 'vue'
    import { useRoute } from 'vue-router'

    import { getAnvarligNames } from '@/services/userService'

    const route = useRoute()
    const id = parseInt(route.query.id, 10)
    const isSubmitting = ref(false)

    const inputFields = ref({
        name: '',
        ansvarlig: '',
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

    /* Instantiate */
    onMounted(() => {

        getAnvarligNames().then(data => {
            assistantList.value = data.data.fullnames
        }).catch(error => {
            console.error('Error fetching assistant names:', error)
        })

        // if (keycloak.authenticated) {
        //     if(keycloak.tokenParsed?.name) {
        //         // Automatically select logged in admin
        //         loggedInAdmin.value = keycloak.tokenParsed?.name
        //         selectAdmin(loggedInAdmin.value)
        //     }
        // }
    })
</script>

<template>
    <p class="indent-tiny bold uppercase p-header-adjust">Opret opgave (#{{ id }})</p>

    <form @submit.prevent="submitForm">
    <div class="formContainer">

        <div class="inputContainer">
            <input type="text" id="name" name="name" placeholder=" " v-model="inputFields.name" required>
            <label for="name" class="floating-label">Opgavens navn</label>
        </div>
        
        <div class="inputContainer">
            <input type="text" id="assistant" name="assistant" placeholder=" " @input="searchAssistants(inputFields.ansvarlig)" v-model="inputFields.ansvarlig" class="locked" required :disabled="isAssistantLocked">
            <label for="assistant" class="floating-label">Ansvarlig medarbejder</label>
            <div class="icon" @click="toggleassistantSearch()"><i :class="'fa-solid fa-lock' + (isAssistantLocked ? '' : '-open')"></i></div>
            
            <div class="itemSelector float-right" v-if="isAssistantSearchOpen">
                <span class="float-header small uppercase">Vælg en ansvarlig medarbejder ...</span>
                <div v-for="result in assistantSearchResults" @click="selectAssistant(result)">{{result}}</div>
                <div v-if="assistantSearchResults.length == 0" class="nohover small">Der blev ikke fundet nogle resultater.</div>
            </div>
        </div>

        <div :class="['inputContainer', 'submit', { 'hideOnMobile': isAssistantSearchOpen }]">
            <button :class="['button', 'button-outline', { 'disabled': isSubmitting }]" type="submit" :disabled="isSubmitting">Opret opgave</button>
        </div>

    </div>
    </form>
</template>