<script setup>
    import { ref, onMounted } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
	
    import { createForloebsskabelon } from '@/services/forløbsskabelonService'

    const route = useRoute()
	const router = useRouter()

    const isSubmitting = ref(false)
	const isUrlValid = ref(true)

	const inputFields = ref({
        name: "",
        varighed: ""
    })

	/* Instantiate */

	onMounted(() => {
        if(!opgave_id) {
            console.error('No ID provided')
            router.back()
            return
        }
    })

	/* Submit */

	const submitForm = async () =>
    {
		evaluateUrl(inputFields.value.url)
		if (!isUrlValid.value)
			return;

        isSubmitting.value = true
        try {
			if (isTemplate)
				inputFields.value.OpgaveskabelonID = opgave_id
			else
				inputFields.value.OpgaveID = opgave_id

            const formData = { ...inputFields.value }

            const response = await createForloebsskabelon(formData)
            if(response !== null)
            {
                if (router.getRoutes()[router.getRoutes().length-1].name == "TemplateOverview")
                    router.back()
                else
                    router.replace({ path: '/template-overview' })
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
	<p class="indent-tiny bold uppercase p-header-adjust">Opret forløbsskabelon</p>

	<form @submit.prevent="submitForm">
	<div class="formContainer">

		<div class="inputContainer">
			<input type="text" id="title" name="title" placeholder=" " v-model="inputFields.name" required>
			<label for="title" class="floating-label">Forløbsskabelonens navn</label>
		</div>

		<div class="inputContainer">
			<input type="datetime-local" id="duration" name="duration" placeholder=" " v-model="inputFields.varighed" required>
			<label for="duration" class="floating-label">Forløbets varighed</label>
		</div>

		<div class="inputContainer submit">
			<button class="button button-outline" type="submit" :disabled="isSubmitting">+ Opret forløbsskabelon</button>
		</div>

	</div>
	</form>
</template>