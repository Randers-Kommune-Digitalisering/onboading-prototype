<script setup>
    import { ref, onMounted } from 'vue'
    import { useRoute, useRouter } from 'vue-router'

    import { getUsers } from '@/services/userService.js'
    import { createOpgave, getOpgaveById, updateOpgave, createOpgaveWithOpgaveskabelon } from '@/services/opgaveService.js'
    import { createOpgaveskabelon, getOpgaveskabelonById, updateOpgaveskabelon, getOpgaveskabeloner } from '@/services/opgaveskabelonService.js'
    import { getForloebById } from '@/services/forløbService.js'
    import { getForloebsskabeloner } from '@/services/forløbsskabelonService.js'

    const route = useRoute()
    const router = useRouter()

    const forloeb = ref(null)
    const forloeb_id = ref(parseInt(route.query.id ?? route.query.tid, 10))
    const isTemplate = route.query.template === 'true'  // Whether we are adding an opgave to a forløb/forløbsskablon or creating a template
    const addToTemplate = ref(route.query.tid != null) // Whether we are adding an opgave to a forløbsskabelon
    const isPreparation = ref(!isTemplate && route.query.prep === 'true') // Whether the forløb is under preparation (only relevant if not a template)
    const isSubmitting = ref(false)
    const isEditing = route.query.edit === 'true'
    const opgaveId = isEditing ? parseInt(route.query.id, 10) : null
    const templates = ref([])
    const selectedTemplate = ref("")
    const selectedGroup = ref("")
    const isAddingNewGroup = ref(false)
    const isSelectingTemplate = ref(false)

    const inputFields = ref({
        title: "",
        ansvarlig: "",
        beskrivelse: "",
        note: "",
        startdato: "",
        slutdato: "",
        relativ_startdag: 0,
        relativ_slutdag: 1,
        result: false,
        booking: "",
        timestamp: ""
    })

    /* Assistant search */

    const isAssistantLocked = ref(false)
    const assistantList = ref([])
    const assistantSearchResults = ref([])
    const isAssistantSearchOpen = ref(false)
    const selectedAssistant = ref(null)

    const relativStartday = ref(null)
    const relativEndday = ref(null)
    const relativEnddayAtOne = ref(inputFields.value.relativ_slutdag == 1)

    const searchAssistants = (searchString) => {
        if (searchString.length < 3) {
            isAssistantSearchOpen.value = false
            return assistantSearchResults.value = []
        }
        isAssistantSearchOpen.value = true
        return assistantSearchResults.value = assistantList.value
            .filter(assistant => assistant.name.toLowerCase().includes(searchString.toLowerCase()))
            .slice(0, 8)
    }

    const selectAssistant = (assistant) => {
        inputFields.value.ansvarlig = assistant.name
        selectedAssistant.value = assistant
        isAssistantLocked.value = true
        isAssistantSearchOpen.value = false
    }

    const toggleassistantSearch = () => {
        if(assistantList.value.map(user => user.name).includes(inputFields.value.ansvarlig))
        {
            isAssistantLocked.value = !isAssistantLocked.value
            isAssistantSearchOpen.value = false
        }
        else
            isAssistantLocked.value = false
    }

    const clearAssistantIfNotSelected = () => {
        if(!assistantList.value.map(user => user.name).includes(inputFields.value.ansvarlig))
        {
            inputFields.value.ansvarlig = ""
            selectedAssistant.value = null
            isAssistantLocked.value = false
            isAssistantSearchOpen.value = false
        }
    }

    const returnDagOrDage = (days) => {
        return days == 1 || days == -1 ? 'dag' : 'dage'
    }

    /* Textarea */

    const textareaDescription = ref(null)
    const textareaNote = ref(null)

    const resizeTextareasToFitContent = () => {
        resizeTextareaDescriptionToFitContent()
        resizeTextareaNoteToFitContent()
    }

    const resizeTextareaDescriptionToFitContent = () => {
        textareaDescription.value.style.height = 'auto'
        textareaDescription.value.style.height = (textareaDescription.value.scrollHeight) + 'px'
    }

    const resizeTextareaNoteToFitContent = () => {
        textareaNote.value.style.height = 'auto'
        textareaNote.value.style.height = (textareaNote.value.scrollHeight) + 'px'
    }

    /* Use template */

    const selectTemplate = (template) => {
        isSelectingTemplate.value = false
        if(template == null)
        {
            inputFields.value.title = ""
            inputFields.value.beskrivelse = ""
            inputFields.value.note = ""
            inputFields.value.startdato = ""
            inputFields.value.slutdato = ""
            inputFields.value.booking = ""
            if(addToTemplate.value || isPreparation.value)
            {
                inputFields.value.relativ_slutdag = template.relativ_slutdag
                relativEndday.value = inputFields.value.relativ_slutdag
            }
        }
        
        inputFields.value.title = template.title
        inputFields.value.beskrivelse = template.beskrivelse
        inputFields.value.note = template.note
        inputFields.value.startdato = template.startdato
        inputFields.value.slutdato = template.slutdato
        inputFields.value.booking = template.booking
        if(addToTemplate.value || isPreparation.value)
        {
            inputFields.value.relativ_slutdag = template.relativ_slutdag
            relativEndday.value = inputFields.value.relativ_slutdag
        }
    }

    const selectNoTemplateIfNotSelected = () => {
        if(selectedTemplate.value == "")
            selectedTemplate.value = null
    }

    const setEndDateFromTemplate = () => {
        if (selectedTemplate.value && !isPreparation.value) {
            const startDate = new Date(inputFields.value.startdato)
            const daysToAdd = selectedTemplate.value.relativ_slutdag
            var endDate = new Date(startDate)
            endDate.setDate(endDate.getDate() + daysToAdd)
            inputFields.value.slutdato = endDate.toISOString().split('T')[0]
        }
    }

    const toggleSelectTemplate = () => {
        if(!isSelectingTemplate.value && selectedTemplate.value == null)
            selectedTemplate.value = ""
        isSelectingTemplate.value = !isSelectingTemplate.value
    }

    const selectGroup = (group) => {
        inputFields.value.OpgaveGruppeID = group?.OpgaveGruppeID || null
    }

    const selectNoGroupIfNotSelected = () => {
        if(selectedGroup.value == "")
            selectedGroup.value = null
    }

    const toggleAddNewGroup = () => {
        isAddingNewGroup.value = !isAddingNewGroup.value

        if(isAddingNewGroup.value) {
            inputFields.value.OpgaveGruppeNavn = ""
            selectedGroup.value = null
        } else {
            delete inputFields.value.OpgaveGruppeNavn
            selectedGroup.value = inputFields.value.gruppe.OpgaveGruppeID || null
        }
    }

    /* Instantiate */

    onMounted(() => {
        if(!forloeb_id.value && (!isEditing && !isTemplate)) {
            console.error('No ID provided')
            router.back()
            return
        }

        // Get assistants
        if(!isTemplate && !addToTemplate.value)
            getUsers().then(response => {
                assistantList.value = response.data
            }).catch(error => {
                console.error('Error fetching assistant names:', error)
            })

        // Get templates
        if(!isTemplate && !isEditing)
            getOpgaveskabeloner().then(response => {
                templates.value = response.data
            }).catch(error => {
                console.error('Error fetching forløbsskabeloner:', error)
            })

        // In case we are editing an existing opgave, get values
        if (isEditing) {
            if(isTemplate)
                getOpgaveskabelonById(opgaveId).then(response => {
                    forloeb_id.value = response.data.ForløbID || response.data.ForløbsskabelonID
                    addToTemplate.value = response.data.ForløbsskabelonID != null
                    const formattedData = {
                        ...response.data
                    }
                    Object.assign(inputFields.value, formattedData)
                    relativEnddayAtOne.value = inputFields.value.relativ_slutdag == 1
                })
                .then(() => getForloebValues())
                .then(() => resizeTextareasToFitContent())
                .catch(error => {
                    console.error('Error fetching opgave:', error)
                })
            else
                getOpgaveById(opgaveId).then(response => {
                    forloeb_id.value = response.data.ForløbID || response.data.ForløbsskabelonID
                    addToTemplate.value = response.data.ForløbsskabelonID != null
                    const formattedData = {
                        ...response.data,
                        startdato: response.data.startdato ? response.data.startdato.split('T')[0] : '',
                        slutdato: response.data.slutdato ? response.data.slutdato.split('T')[0] : '',
                        booking: response.data.booking ? response.data.booking.split('T').join(' ') : ''
                    }
                    Object.assign(inputFields.value, formattedData)
                    relativEnddayAtOne.value = inputFields.value.relativ_slutdag == 1
                    isAssistantLocked.value = response.data.ansvarligEmail != ""
                    selectedGroup.value = response.data.gruppe?.OpgaveGruppeID || null
                })
                .then(() => getForloebValues())
                .then(() => resizeTextareasToFitContent())
                .catch(error => {
                    console.error('Error fetching opgave:', error)
                })
        }
        else
            getForloebValues()

        // Get forløb values
        function getForloebValues()
        {
            if(addToTemplate.value == true)
                getForloebsskabeloner().then(response => {
                    forloeb.value = response.data.filter(skabelon => skabelon.ForløbsskabelonID == forloeb_id.value)[0]
                }).catch(error => {
                    console.error('Error fetching forløbsskabelon:', error)
                })
            else if(forloeb_id.value) {
                getForloebById(forloeb_id.value).then(response => {
                    forloeb.value = response.data
                }).catch(error => {
                    console.error('Error fetching forløb:', error)
                })
            }
        }
    })

    /* Submit */

    const removeNonIntegers = (value) => {
        // Allow a single minus at the start, then digits only
        return value.replace(/(?!^-\d*)[^\d-]|(?!^)-/g, '').replace(/(?!^)-/g, '')
    }

    const sliceXChars = (value, x) => {
        return value.slice(0, x)
    }

    const submitForm = async () =>
    {     
        isSubmitting.value = true
        try {
            inputFields.value.timestamp = new Date().toISOString()
            if(addToTemplate.value)
                inputFields.value.ForløbsskabelonID = forloeb_id.value
            else
                inputFields.value.ForløbID = forloeb_id.value
            if(!isTemplate)
                inputFields.value.ansvarligEmail = selectedAssistant.value?.email ?? ""
            if(selectedTemplate.value != null)
                inputFields.value.OpgaveskabelonID = selectedTemplate.value.OpgaveskabelonID

            inputFields.value.OpgaveGruppeID = selectedGroup.value
            if(inputFields.value.OpgaveGruppeNavn)
                delete inputFields.value.OpgaveGruppeID

            const formData = { 
                ...inputFields.value
            }

            if(isTemplate || addToTemplate.value || isPreparation.value)
                delete formData.startdato, delete formData.slutdato, delete formData.booking
            else
                delete formData.relativ_startdag, delete formData.relativ_slutdag
                if(formData.booking == "")
                    delete formData.booking
            
            const response = isEditing ?
                                (isTemplate ?
                                    await updateOpgaveskabelon(opgaveId, formData)
                                  : await updateOpgave(opgaveId, formData))
                              : (isTemplate ?
                                    await createOpgaveskabelon(formData)
                                  : selectedTemplate.value != null ?
                                        await createOpgaveWithOpgaveskabelon(formData)
                                      : await createOpgave(formData))
            
            if(response !== null)
                returnToPrevious(response?.data?.OpgaveID)
            else
                console.error('Response:', response)

        } catch (error) {            
            console.error('Error:', error.response?.data?.error ?? error)
        }
        isSubmitting.value = false
    }

    const returnToPrevious = (id = null) =>
	{
		// Get last route
		let lastUrl = router.options.history.state.back
		let lastRoute = router.getRoutes().find(route => route.path == lastUrl.split('?')[0])
		lastRoute.query = Object.fromEntries(new URLSearchParams(lastUrl.split('?')[1]))

		// Add query params
		lastRoute.query = { ...lastRoute.query, item: id ?? opgaveId }

		// Go back
		router.replace({ path: lastRoute.path, query: lastRoute.query })
	}
</script>

<template>
    <p class="indent-tiny bold uppercase p-header-adjust">
        {{ isEditing ? 'Rediger opgave' : isTemplate ? 'Opret opgaveskabelon' : 'Tilføj opgave' }}
        {{ isTemplate ? '' : ' til ' + forloeb?.name?? 'forløbet' }}
    </p>

    <form @submit.prevent="submitForm">
    <div class="formContainer">

        <template v-if="!isEditing && !isTemplate && isSelectingTemplate">
            <div class="inputContainer">
                <select id="template" name="template" v-model="selectedTemplate" @change="selectTemplate(selectedTemplate)" required>
                    <option value="" disabled selected hidden></option>
                    <option :value="null" style="color:gray">Ingen skabelon</option>
                    <option v-for="template in templates" :value="template">{{template.title}}</option>
                </select>
                <label for="template" class="floating-label">Skabelon</label>
                <div class="icon nohover adjust-for-button"><i class="fa-solid fa-caret-down"></i></div>
                <div class="button input-button tooltip-hover" @click="toggleSelectTemplate()">
                    <i class="fa-solid fa-arrow-left"></i>
                    <span class="tooltip-display nohover">Fortryd</span>
                </div>
            </div>

        </template>

        <template v-else>
            <div class="inputContainer">
                <input type="text" id="title" name="title" placeholder=" " v-model="inputFields.title" required>
                <label for="title" class="floating-label">Opgavens navn</label>
                <div class="button input-button tooltip-hover" @click="toggleSelectTemplate()">
                    <i class="fa-solid fa-folder"></i>
                    <span class="tooltip-display nohover">Vælg skabelon</span>
                </div>
            </div>
            
            <div class="inputContainer" v-if="!isTemplate && !addToTemplate">
                <input type="text" id="assistant" name="assistant" placeholder=" " @input="searchAssistants(inputFields.ansvarlig)" v-model="inputFields.ansvarlig" class="locked" :disabled="isAssistantLocked">
                <label for="assistant" class="floating-label">Ansvarlig medarbejder</label>
                <div class="icon" @click="toggleassistantSearch()"><i :class="'fa-solid fa-lock' + (isAssistantLocked ? '' : '-open')"></i></div>
                
                <div class="itemSelector float-right" v-if="isAssistantSearchOpen">
                    <span class="float-header small uppercase">Vælg en ansvarlig medarbejder ...</span>
                    <div v-for="result in assistantSearchResults" @click="selectAssistant(result)">{{result.name}}</div>
                    <div v-if="assistantSearchResults.length == 0" class="nohover small">Der blev ikke fundet nogle resultater.</div>
                </div>
            </div>

            <div :class="['inputContainer', { 'hideOnMobile': isAssistantSearchOpen }]">
                <textarea id="description" name="description" ref="textareaDescription" @input="resizeTextareaDescriptionToFitContent()" placeholder=" " v-model="inputFields.beskrivelse" required></textarea>
                <label for="description" class="floating-label">Beskrivelse</label>
            </div>

            <div :class="['inputContainer', { 'hideOnMobile': isAssistantSearchOpen }]">
                <textarea id="note" name="note" ref="textareaNote" @input="resizeTextareaNoteToFitContent()" placeholder=" " v-model="inputFields.note"></textarea>
                <label for="note" class="floating-label">Note til ansvarlig</label>
            </div>

            <div :class="['inputContainer', { 'hideOnMobile': isAssistantSearchOpen }]" v-if="!isTemplate">
                <input v-if="isAddingNewGroup" type="text" id="gruppe" name="gruppe" placeholder="" v-model="inputFields.OpgaveGruppeNavn" required>
                <select v-else id="gruppe" name="gruppe" v-model="selectedGroup" @change="selectGroup(selectedGroup)" required>
                    <option value="" disabled selected hidden></option>
                    <option :value="null" style="color:gray">Ingen gruppe</option>
                    <option v-for="gruppe in forloeb?.opgave_grupper" :value="gruppe.OpgaveGruppeID">{{gruppe.name}}</option>
                </select>
                <label for="gruppe" class="floating-label">{{ isAddingNewGroup ? 'Nyt gruppenavn' : 'Gruppe' }}</label>
                <div v-if="!isAddingNewGroup" class="icon nohover" style="transform: translateX(-4rem);"><i class="fa-solid fa-caret-down"></i></div>
                <div class="button input-button tooltip-hover" @click="toggleAddNewGroup()">
                    <i v-if="isAddingNewGroup" class="fa-solid fa-arrow-left"></i>
                    <i v-else class="fa-solid fa-plus"></i>
                    <span class="tooltip-display nohover">{{ isAddingNewGroup ? 'Fortryd' : 'Opret skabelon' }}</span>
                </div>
            </div>

            <div :class="['inputContainer', { 'hideOnMobile': isAssistantSearchOpen }]" v-if="!isTemplate && !addToTemplate && !isPreparation">
                <div class="flex-item">
                    <input type="date" id="startdate" name="startdate" v-model="inputFields.startdato" @change="setEndDateFromTemplate()" required>
                    <label for="startdate" class="floating-label">Startdato</label>
                </div>
                <div class="flex-item">
                    <input type="date" id="enddate" name="enddate" v-model="inputFields.slutdato" required>
                    <label for="enddate" class="floating-label">Slutdato</label>
                </div>
            </div>

            
            <div :class="['inputContainer', { 'hideOnMobile': isAssistantSearchOpen }]" v-if="!isTemplate && !addToTemplate && !isPreparation">
                <input type="datetime-local" id="booking" name="booking" v-model="inputFields.booking">
                <label for="booking" class="floating-label">Booking</label>
            </div>

            <!--  Relative start and end days -->
            <div :class="['inputContainer', { 'hideOnMobile': isAssistantSearchOpen }]" v-if="isTemplate || addToTemplate || isPreparation">
                <div v-if="addToTemplate || isPreparation" class="flex-item">
                    <input type="text" id="startdate" class="padding-input" name="startdate"
                            v-model="inputFields.relativ_startdag" ref="relativStartday"
                            @input="relativStartday.value=sliceXChars(removeNonIntegers(relativStartday.value), 3)"
                            required>
                    <label for="startdate" class="floating-label">Startes efter </label>
                    <label for="startdate" class="annot-label">{{ returnDagOrDage(inputFields.relativ_startdag) }}</label>
                    <div :class="['floating-button', 'indent-floating-button']"
                            @click="inputFields.relativ_startdag--">
                                <i class="fa fa-minus"></i>
                            </div>
                    <div class="floating-button" 
                        @click="inputFields.relativ_startdag++">
                        <i class="fa fa-plus"></i>
                    </div>
                </div>
                <div class="flex-item">
                    <input type="text" id="enddate" class="padding-input" name="enddate"
                            v-model="inputFields.relativ_slutdag" ref="relativEndday"
                            @input="relativEndday.value=inputFields.relativ_slutdag=Math.max(1, sliceXChars(removeNonIntegers(relativEndday.value), 3));relativEnddayAtOne = inputFields.relativ_slutdag==1"
                            required>
                    <label for="enddate" class="floating-label">Varighed</label>
                    <label for="enddate" class="annot-label">{{ returnDagOrDage(inputFields.relativ_slutdag) }}</label>
                    <div :class="['floating-button', 'indent-floating-button', { 'disabled': relativEnddayAtOne}]"
                            @click="inputFields.relativ_slutdag--;relativEnddayAtOne = inputFields.relativ_slutdag==1">
                            <i class="fa fa-minus"></i>
                        </div>
                    <div class="floating-button" @click="relativEnddayAtOne = false;inputFields.relativ_slutdag++">
                        <i class="fa fa-plus"></i>
                    </div>
                </div>
            </div>

            <div :class="['inputContainer', 'submit', { 'hideOnMobile': isAssistantSearchOpen }]">
                <button :class="['button', 'button-outline', { 'disabled': isSubmitting }]"
                        type="submit"
                        @click="clearAssistantIfNotSelected();selectNoTemplateIfNotSelected();selectNoGroupIfNotSelected()"
                        :disabled="isSubmitting">
                            {{ isEditing ? 'Opdater opgave' : isTemplate ? '+ Opret opgaveskabelon' : '+ Tilføj opgave' }}
                </button>
            </div>
        </template>

    </div>
    </form>
</template>
<style scoped>
    .annot-label {
        left: calc(45% - 0.5rem);
        bottom: 0.6rem;
    }
    .indent-floating-button {
        right: 2.7rem;
    }
    .padding-input {
        padding-left: calc(45% - 2.5rem);
    }
    .input-button {
        border-radius: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .tooltip-display
    {
        transform: translate(0, -2.6rem);
        width: auto;
        white-space: nowrap;
    }
    .icon.adjust-for-button {
        transform: translateX(-4rem);
    }
</style>