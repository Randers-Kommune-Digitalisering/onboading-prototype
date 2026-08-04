<script setup>
    import { ref, onMounted, nextTick } from 'vue'
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
    const focusedInput = ref(null)

    const inputFields = ref({
        title: "",
        ansvarlig: "",
        beskrivelse: "",
        note: "",
        hidden: false,
        startdato: "",
        slutdato: "",
        relativ_startdag: 0,
        relativ_slutdag: 1,
        result: false,
        booking: "",
        timestamp: ""
    })

    const inputFieldDescriptions = ref({
        title: { text: "Opgavens navn", tooltip: "<span>Giv opgaven et beskrivende navn.</span><span>Navnet vil være synligt i forløbets opgaveoverblik.</span>" },
        ansvarlig: { text: "Ansvarlig medarbejder", tooltip: "<span>Vælg den medarbejder, der skal hjælpe den nye medarbejder med denne opgave (f.eks. introducere, vejlede eller løse opgaven sammen).</span><span>Det er også den ansvarlige, der efterfølgende skal markere opgaven som udført.</span>" },
        beskrivelse: { text: "Beskrivelse", tooltip: "<span>Giv en detaljeret beskrivelse af opgaven.</span><span>Beskrivelsen er synlig både for den nye medarbejder samt en eventuel ansvarlig medarbejder.</span>" },
        note: { text: "Note til ansvarlig", tooltip: "<span>Tilføj eventuelle noter til den ansvarlige medarbejder.</span><span>Noten vil kun være synlig for den ansvarlige medarbejder, og kan ikke læses af den nye medarbejder.</span>" },
        hidden: { text: "Skjult opgave", tooltip: "<span>Når slået til, vises opgaven kun for administratorer og den ansvarlige medarbejder.</span><span>Skjulte opgaver tæller ikke med i forløbets gennemførelsesprocent.</span>" },
        gruppe: { text: "Opgavegruppe", tooltip: "<span>Vælg en opgavegruppe for at gruppere denne opgave med andre opgaver i forløbet.</span><span>Opgaver kan sorteres efter gruppe i forløbets opgaveoverblik, hvilket kan hjælpe med at skabe overblik i forløb med mange opgaver.</span>" },
        nygruppe: { text: "Ny opgavegruppe", tooltip: "<span>Giv den nye opgavegruppe et beskrivende navn.</span><span>Du kan efterfølgende tilføje flere opgaver til denne gruppe for at skabe bedre overblik over opgaverne i forløbet.</span>" },
        startdato: { text: "Startdato", tooltip: "<span>Vælg startdato for opgaven.</span><span>Startdato sættes til den dag, hvor opgaven skal påbegyndes.</span>" },
        slutdato: { text: "Slutdato", tooltip: "<span>Vælg slutdato for opgaven.</span><span>Slutdato fungerer som en deadline for opgaven, og sættes til den dag, opgaven skal være afsluttet inden.</span><span>Slutdato kan tidligst sættes til dagen efter startdato for opgaven.</span>" },
        relativ_startdag: { text: "Relativ startdag", tooltip: "<span>Angiv relativ startdag for opgaven.</span><span>Relativ startdag bruges til at beregne startdatoen baseret på forløbets startdato.</span>" },
        relativ_slutdag: { text: "Relativ slutdag", tooltip: "<span>Angiv relativ slutdag for opgaven.</span><span>Relativ slutdag bruges til at beregne opgavens slutdato baseret på startdatoen, som tildeles når skabelonen omsættes til en opgave.</span>" },
        booking: { text: "Bookingtidspunkt", tooltip: "<span>Angiv bookingtidspunkt for opgaven.</span><span>Bookingtidspunkt bruges til at indikere hvornår den ansvarlige medarbejder skal hjælpe med opgaven, eller hvornår der er afsat tid til opgaven.</span><span><b>OBS</b>: Der oprettes ikke automatisk en aftale i kalenderen.</span>" }
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

    const onSetStartDate = () => {
        if(inputFields.value.startdato == inputFields.value.slutdato) {
            // Advance slutdato by 1 day if startdato and slutdato are the same
            _advanceEndDateByOneDay()
        }
        // If startdate is after enddate, clear enddate
        else if(inputFields.value.startdato > inputFields.value.slutdato)
            inputFields.value.slutdato = ""
    }

    const onSetEndDate = () => {
        if(inputFields.value.slutdato == inputFields.value.startdato) {
            // Advance slutdato by 1 day if startdato and slutdato are the same
            _advanceEndDateByOneDay()
        }
        // If enddate is before startdate, clear startdate
        else if(inputFields.value.slutdato < inputFields.value.startdato)
            inputFields.value.startdato = ""
    }

    const _advanceEndDateByOneDay = () => {
        const date = new Date(inputFields.value.slutdato)
        date.setDate(date.getDate() + 1)
        inputFields.value.slutdato = date.toISOString().split('T')[0]
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
            inputFields.value.hidden = false
            inputFields.value.startdato = ""
            inputFields.value.slutdato = ""
            inputFields.value.booking = ""
            inputFields.value.hidden = false
            if(addToTemplate.value || isPreparation.value)
            {
                inputFields.value.relativ_slutdag = 1
                relativEndday.value = inputFields.value.relativ_slutdag
            }
            return
        }
        
        inputFields.value.title = template.title
        inputFields.value.beskrivelse = template.beskrivelse
        inputFields.value.note = template.note
        inputFields.value.hidden = template.hidden === true
        inputFields.value.startdato = template.startdato
        inputFields.value.slutdato = template.slutdato
        inputFields.value.booking = template.booking
        inputFields.value.hidden = template.hidden === true
        if(addToTemplate.value || isPreparation.value)
        {
            inputFields.value.relativ_slutdag = template.relativ_slutdag
            relativEndday.value = inputFields.value.relativ_slutdag
        }
        nextTick(() => {
            resizeTextareasToFitContent()
            resizeTextareaDescriptionToFitContent()
        })
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
        return value.replace(/[^-\d]/g, '').replace(/(?!^)-/g, '')
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

            if(inputFields.value.hidden === true)
                formData.note = null
            
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
        if (router.currentRoute.value.path.startsWith('/forloeb-overview/')) {
            const parentForloebId = route.query.forloebTid || route.query.forloebId || forloeb_id.value
            const returnToTemplateOverview = route.query.forloebTid != null || route.query.tid != null
            const nextQuery = {
                ...router.currentRoute.value.query,
                item: id ?? opgaveId,
                refreshTasks: Date.now().toString(),
            }

            if (returnToTemplateOverview)
                nextQuery.tid = parentForloebId
            else
                nextQuery.id = parentForloebId

            // In nested edit flows, `id` may still be the task id from the editor URL.
            // Keep task selection in `item` and avoid leaking stale task id as forloeb id.
            if (returnToTemplateOverview)
                delete nextQuery.id

            delete nextQuery.edit
            delete nextQuery.forloebId
            delete nextQuery.forloebTid
            router.replace({ path: '/forloeb-overview', query: nextQuery })
            return
        }

		// Get last route
		let lastUrl = router.options.history.state.back
        if (!lastUrl) {
            router.replace({
                path: '/forloeb-overview',
                query: {
                    id: forloeb_id.value,
                    item: id ?? opgaveId,
                    refreshTasks: Date.now().toString(),
                },
            })
            return
        }

		let lastRoute = router.getRoutes().find(route => route.path == lastUrl.split('?')[0])
        if (!lastRoute) {
            router.replace({
                path: '/forloeb-overview',
                query: {
                    id: forloeb_id.value,
                    item: id ?? opgaveId,
                    refreshTasks: Date.now().toString(),
                },
            })
            return
        }
		lastRoute.query = Object.fromEntries(new URLSearchParams(lastUrl.split('?')[1]))

		// Add query params
		lastRoute.query = { ...lastRoute.query, item: id ?? opgaveId }

		// Go back
		router.replace({ path: lastRoute.path, query: lastRoute.query })
	}
</script>

<template>
    <div class="flex"><div class="max-width"><!-- wrapper -->

    <p class="indent-tiny bold uppercase p-header-adjust">
        {{ isEditing ? 'Rediger opgave' : isTemplate ? 'Opret opgaveskabelon' : 'Tilføj opgave' }}
        {{ isTemplate ? '' : ' til ' + (forloeb?.name ?? 'forløbet') }}
    </p>

    <div
        v-if="focusedInput && !isAssistantSearchOpen"
        class="float-right helper-text"
        @mousedown.prevent
        @click.prevent
    >
		<div class="header-small">{{ focusedInput.text }}</div>
        <div v-html="focusedInput.tooltip"></div>
    </div>

    <form @submit.prevent="submitForm">
    <div class="formContainer float-right-gutter">

        <template v-if="!isEditing && !isTemplate && isSelectingTemplate">
            <div class="inputContainer">
                <select id="template" name="template" v-model="selectedTemplate" @change="selectTemplate(selectedTemplate)" required>
                    <option value="" disabled selected hidden></option>
                    <option :value="null" style="color:gray">Ingen skabelon</option>
                    <option v-for="template in templates" :value="template">{{template.title ? template.title + ' | ' : ''}}{{template.beskrivelse ? template.beskrivelse.substring(0, 50) + (template.beskrivelse.length > 50 ? '...' : '') : ''}}</option>
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
                <input
                    type="text" id="title" name="title"
                    placeholder=" "
                    v-model="inputFields.title"
                    @focus="focusedInput = inputFieldDescriptions.title"
                    @blur="focusedInput = null">
                <label for="title" class="floating-label">Opgavens navn</label>
                <div class="button input-button tooltip-hover" @click="toggleSelectTemplate()" v-if="!isEditing && !isTemplate">
                    <i class="fa-solid fa-folder"></i>
                    <span class="tooltip-display nohover">Vælg skabelon</span>
                </div>
            </div>

            <div :class="['inputContainer']" v-if="!isTemplate">
                <input
                    type="text" id="gruppe" name="gruppe" 
                    v-if="isAddingNewGroup"
                    placeholder=""
                    v-model="inputFields.OpgaveGruppeNavn"
                    @focus="focusedInput = inputFieldDescriptions.nygruppe"
                    @blur="focusedInput = null"
                    required>
                <select
                    id="gruppe" name="gruppe" 
                    v-else
                    v-model="selectedGroup"
                    @change="selectGroup(selectedGroup)"
                    @focus="focusedInput = inputFieldDescriptions.gruppe"
                    @blur="focusedInput = null"
                    required>
                    <option value="" disabled selected hidden></option>
                    <option :value="null" style="color:gray">Ingen gruppe</option>
                    <option v-for="gruppe in forloeb?.opgave_grupper" :value="gruppe.OpgaveGruppeID">{{gruppe.name}}</option>
                </select>
                <label for="gruppe" class="floating-label">{{ isAddingNewGroup ? 'Nyt gruppenavn' : 'Gruppe' }}</label>
                <div v-if="!isAddingNewGroup" class="icon nohover" style="transform: translateX(-4rem);"><i class="fa-solid fa-caret-down"></i></div>
                <div class="button input-button tooltip-hover" @click="toggleAddNewGroup()">
                    <i v-if="isAddingNewGroup" class="fa-solid fa-arrow-left"></i>
                    <i v-else class="fa-solid fa-plus"></i>
                    <span class="tooltip-display nohover">{{ isAddingNewGroup ? 'Fortryd' : 'Opret gruppe' }}</span>
                </div>
            </div>

            <div class="inputContainer" v-if="!isTemplate && !addToTemplate">
                <input
                    type="text" id="assistant" name="assistant"
                    placeholder=" "
                    @input="searchAssistants(inputFields.ansvarlig)"
                    v-model="inputFields.ansvarlig" class="locked"
                    :disabled="isAssistantLocked"
                    @focus="focusedInput = inputFieldDescriptions.ansvarlig"
                    @blur="focusedInput = null">
                <label for="assistant" class="floating-label">Ansvarlig medarbejder</label>
                <div class="icon" @click="toggleassistantSearch()"><i :class="'fa-solid fa-lock' + (isAssistantLocked ? '' : '-open')"></i></div>
                
                <div class="itemSelector float-right" v-if="isAssistantSearchOpen">
                    <span class="float-header small uppercase">Vælg en ansvarlig medarbejder ...</span>
                    <div v-for="result in assistantSearchResults" @click="selectAssistant(result)">{{result.name}}</div>
                    <div v-if="assistantSearchResults.length == 0" class="nohover small">Der blev ikke fundet nogle resultater.</div>
                </div>
            </div>

            <div :class="['inputContainer', { 'hideOnMobile': isAssistantSearchOpen }]">
                <textarea
                    id="description" name="description"
                    ref="textareaDescription"
                    @input="resizeTextareaDescriptionToFitContent()"
                    placeholder=" "
                    v-model="inputFields.beskrivelse"
                    @focus="focusedInput = inputFieldDescriptions.beskrivelse"
                    @blur="focusedInput = null"
                    required></textarea>
                <label for="description" class="floating-label">Beskrivelse</label>
            </div>

            <div :class="['inputContainer checkbox', { 'hideOnMobile': isAssistantSearchOpen }]">
                <input
                    type="checkbox"
                    id="hidden"
                    name="hidden"
                    v-model="inputFields.hidden"
                    @focus="focusedInput = inputFieldDescriptions.hidden"
                    @blur="focusedInput = null">
                <label for="hidden" class="checkbox-label">
                    Skjult opgave (kun admin + ansvarlig)
                </label>
            </div>

            <div v-if="!inputFields.hidden" :class="['inputContainer', { 'hideOnMobile': isAssistantSearchOpen }]">
                <textarea
                    id="note" name="note"
                    ref="textareaNote"
                    @input="resizeTextareaNoteToFitContent()"
                    placeholder=" "
                    v-model="inputFields.note"
                    @focus="focusedInput = inputFieldDescriptions.note"
                    @blur="focusedInput = null"></textarea>
                <label for="note" class="floating-label">Note til ansvarlig</label>
            </div>

            <div :class="['inputContainer', { 'hideOnMobile': isAssistantSearchOpen }]" v-if="!isTemplate && !addToTemplate && !isPreparation">
                <div class="flex-item">
                    <input
                        type="date" id="startdate" name="startdate"
                        v-model="inputFields.startdato"
                        @change="onSetStartDate();setEndDateFromTemplate()"
                        @focus="focusedInput = inputFieldDescriptions.startdato"
                        @blur="focusedInput = null"
                        required>
                    <label for="startdate" class="floating-label">Startdato</label>
                </div>
                <div class="flex-item">
                    <input type="date" id="enddate" name="enddate"
                    v-model="inputFields.slutdato"
                    @change="onSetEndDate()"
                    @focus="focusedInput = inputFieldDescriptions.slutdato"
                    @blur="focusedInput = null"
                    required>
                    <label for="enddate" class="floating-label">Slutdato</label>
                </div>
            </div>


            <div :class="['inputContainer', { 'hideOnMobile': isAssistantSearchOpen }]" v-if="!isTemplate && !addToTemplate && !isPreparation">
                <input
                    type="datetime-local"
                    id="booking" name="booking"
                    v-model="inputFields.booking"
                    @focus="focusedInput = inputFieldDescriptions.booking"
                    @blur="focusedInput = null">
                <label for="booking" class="floating-label">Booking</label>
            </div>

            <!--  Relative start and end days -->
            <div :class="['inputContainer', { 'hideOnMobile': isAssistantSearchOpen }]" v-if="isTemplate || addToTemplate || isPreparation">
                <div v-if="addToTemplate || isPreparation" class="flex-item">
                    <input type="text" id="startdate" class="padding-input" name="startdate"
                            v-model="inputFields.relativ_startdag" ref="relativStartday"
                            @input="relativStartday.value=inputFields.relativ_startdag=sliceXChars(removeNonIntegers(relativStartday.value), 3)"
                            @focus="focusedInput = inputFieldDescriptions.relativ_startdag"
                            @blur="focusedInput = null"
                            required>
                    <label for="startdate" class="floating-label">Startes</label>
                    <label for="startdate" class="annot-label">{{ returnDagOrDage(inputFields.relativ_startdag) }}{{ inputFields.relativ_startdag < 0 ? ' før opstart' : ' efter opstart' }}</label>
                    <div :class="['floating-button', 'indent-floating-button', { 'disabled': inputFields.relativ_startdag <= -99 }]"
                            @click="inputFields.relativ_startdag--">
                                <i class="fa fa-minus"></i>
                            </div>
                    <div :class="['floating-button', { 'disabled': inputFields.relativ_startdag >= 999 }]" 
                        @click="inputFields.relativ_startdag++">
                        <i class="fa fa-plus"></i>
                    </div>
                </div>
                <div class="flex-item">
                    <input type="text" id="enddate" class="padding-input" name="enddate"
                            v-model="inputFields.relativ_slutdag" ref="relativEndday"
                            @input="relativEndday.value=inputFields.relativ_slutdag=Math.max(1, sliceXChars(removeNonIntegers(relativEndday.value), 3));relativEnddayAtOne = inputFields.relativ_slutdag==1"
                            @focus="focusedInput = inputFieldDescriptions.relativ_slutdag"
                            @blur="focusedInput = null"
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
                <button :class="['button', { 'disabled': isSubmitting }]"
                        type="submit"
                        @click="clearAssistantIfNotSelected();selectNoTemplateIfNotSelected();selectNoGroupIfNotSelected()"
                        :disabled="isSubmitting">
                            {{ isEditing ? 'Opdater opgave' : isTemplate ? '+ Opret opgaveskabelon' : '+ Tilføj opgave' }}
                </button>
            </div>
        </template>

    </div>
    </form>

    </div></div><!-- /wrapper -->
</template>
<style scoped>
    .annot-label {
        left: 2.5rem;
        bottom: 0.6rem;
    }
    .indent-floating-button {
        right: 2.7rem;
    }
    .input-button {
        border-radius: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .icon.adjust-for-button {
        transform: translateX(-4rem);
    }
</style>