<script setup>
    import { ref, onMounted, nextTick, computed } from 'vue'
    import { useRouter, useRoute } from 'vue-router'
    import { getForloebById } from '@/services/forløbService.js'
    import { sendWelcomeMail } from '../../services/mailService'

    const route = useRoute()
    const router = useRouter()

    const isPreviewing = ref(false)
    const isSubmitting = ref(false)
    const focusedInput = ref(null)

    const forloeb_id = parseInt(route.query.id, 10)

    const textareaContent = ref(null)
    const inputFields = ref({
        usermail: "",
        subject: "Velkommen til Randers Kommune - Dit onboarding-forløb er klar!",
        content: "\
Kære {navn},\n\
\n\
Velkommen til Randers Kommune!\n\
\n\
Dit onboarding-forløb er nu klar, og du kan allerede nu tage et kig på, hvad der venter dig.\n\
\n\
{link} \n\
\n\
Forløbet starter den {startdato}.\n\
\n\
Vi håber, at du får en god start hos os, og at forløbet bliver både lærerigt og spændende.\n\
\n\
Har du spørgsmål eller brug for hjælp inden du starter, er du altid velkommen til at række ud til os.\n\
Du kan bare svare på denne mail, så sørger vi for at hjælpe dig bedst muligt.\n\
\n\
Med venlig hilsen,\n\
Randers Kommune",
    })

    const inputFieldDescriptions = {
        subject: { text: "Emne", tooltip: "<span>Indtast velkomstmailens emne.</span>" },
        content: { text: "Indhold", tooltip: "<span>Indtast det indhold, som skal være i velkomstmailen.</span><span>Du kan bruge følgende variabler, som vil blive erstattet med det relevante indhold for det specifikke forløb.</span><span><b>{navn}</b> - Medarbejderens fornavn</span><span><b>{efternavn}</b> - Medarbejderens efternavn(e)</span><span><b>{link}</b> - Knap med link til forløbet</span><span><b>{startdato}</b> - Forløbets startdato</span><span><b>{slutdato}</b> - Forløbets slutdato</span><span><b>{forløb}</b> - Forløbets navn</span><span><b>{randers kommune}</b> - Randers Kommune med logo" }
    }

    const previewContent = computed(() => {
        if (!isPreviewing.value) return ""
        let content = inputFields.value.content
        content = content.replaceAll(/{navn}/g, "Test")
        content = content.replaceAll(/{efternavn}/g, "Testesen")
        content = content.replaceAll(/{link}/g, '<div style="margin-top: 8px;margin-bottom: 16px;display: inline-block"><a href="#" style="text-decoration: none; background-color: rgb(56, 65, 84); border: 10px solid  rgb(56, 65, 84); color: rgb(237, 229, 220) !important; cursor: pointer; user-select: none; display:block;">Se dit onboarding-forløb</a></div>')
        content = content.replaceAll(/{startdato}/g, "01-01-2024")
        content = content.replaceAll(/{slutdato}/g, "31-12-2024")
        content = content.replaceAll(/{forløb}/g, "Onboarding forløb")
        content = content.replaceAll(/\n/g, "<br>")
        return content
    })

    const resizeTextareaContentToFitContent = () => {
        textareaContent.value.style.height = 'auto'
        textareaContent.value.style.height = (textareaContent.value.scrollHeight) + 'px'
    }



    /* Instantiate */
    onMounted(async () => {
        if (!forloeb_id) {
            router.replace('/admin-overview')
            return
        }

        // Get forløb
        try {
            const forloebResponse = await getForloebById(forloeb_id)
            if(forloebResponse.data?.error || forloebResponse.data?.isPreparation === true || forloebResponse.data?.isTemplate === true) {
                console.error('Error fetching forløb or forløb is template or in preparation:', forloebResponse.data.error)
                router.replace('/admin-overview')
                return
            }
            Object.assign(inputFields.value, forloebResponse.data)
        } catch (error) {
            console.error('Error fetching forløb:', error)
        }

        resizeTextareaContentToFitContent()
    })


    /* Preview and submit */
    const submitForm = async () => {
        if (!isPreviewing.value) {
            isPreviewing.value = true

        } else {
            isSubmitting.value = true
            try {
                const formData = {
                    subject: inputFields.value.subject,
                    content: inputFields.value.content
                }
                console.log('Form Data to be sent:', formData)
                const response = await sendWelcomeMail(forloeb_id, formData)
                if(response)
                    router.replace({ path: '/forloeb-overview', query: { id: forloeb_id } })
                
            } catch (error) {
                if (error.response?.data?.error)
                    console.error('Error:', error.response.data.error)
                else 
                    console.error('Error:', error)
            }
            isSubmitting.value = false
        }
    }

</script>

<template>


    <p class="indent-tiny bold uppercase p-header-adjust">Send velkomstmail</p>


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

         <div class="inputContainer">
            <input type="text" id="mail" name="mail" placeholder=" " v-model="inputFields.usermail" disabled>
            <label for="mail" class="floating-label">Medarbejder mailadresse</label>
        </div>

        
         <div class="inputContainer">
            <input type="text" id="subject" name="subject" placeholder=" " v-model="inputFields.subject" @focus="focusedInput = inputFieldDescriptions.subject" @blur="focusedInput = null" required :disabled="isPreviewing">
            <label for="subject" class="floating-label">Emne</label>
        </div>

        <template v-if="!isPreviewing">

            <div :class="['inputContainer']">
                <textarea
                    id="content" name="content"
                    ref="textareaContent"
                    @input="resizeTextareaContentToFitContent()"
                    placeholder=" "
                    v-model="inputFields.content"
                    @focus="focusedInput = inputFieldDescriptions.content"
                    @blur="focusedInput = null"
                    required></textarea>
                <label for="content" class="floating-label">Indhold</label>
            </div>

            <div class="inputContainer submit">
                <button :class="['button', { 'disabled': isSubmitting }]" type="submit" :disabled="isSubmitting">Se forhåndsvisning</button>
            </div>

        </template>
        <template v-else>
            <div class="previewContainer">
                <div class="previewContent" v-html="previewContent"></div>
                <label for="previewContainer" class="floating-previewContainer-label">Indhold</label>
            </div>

            <div class="inputContainer submit">
                <button :class="['button', 'hollow', { 'disabled': isSubmitting }]" type="submit" @click="isPreviewing = false; nextTick(() => { resizeTextareaContentToFitContent() })">Redigér indhold</button>
                <button :class="['button', { 'disabled': isSubmitting }]" type="submit" :disabled="isSubmitting">Send velkomstmail</button>
            </div>
        </template>

    </div>
    </form>



</template>


<style scoped>
    textarea {
        min-height: 8.2rem;
    }
    .previewContainer {
        position: relative;
        background-color: var(--color-input-disabled-bg);
        width: 100%;
        padding: 1.6rem 0.8rem 0.6rem 0.8rem;
        box-sizing: border-box;
        border-radius: 0.2rem;
        border: 0rem;
        transition-duration: 200ms;
        transition: opacity 0s;
        font-size: 0.8rem;
    }
    .floating-previewContainer-label {
        position: absolute;
        top: 0.5rem;
        left: 0.8rem;
        color: #8b8b8b;
        font-size: 0.8em;
    }
    input:disabled, textarea:disabled {
        color: inherit;
        font-weight: 400;
    }
</style>