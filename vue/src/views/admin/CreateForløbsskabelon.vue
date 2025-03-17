<script setup>
    import { ref, onMounted } from 'vue'
    import { useRouter } from 'vue-router'
	
    import { createForloebsskabelon } from '@/services/forløbsskabelonService'

	const router = useRouter()

    const isSubmitting = ref(false)

	const inputFields = ref({
        name: "",
        varighed: ""
    })
    const varighed = ref(null)

	/* Submit */

	const submitForm = async () =>
    {
        isSubmitting.value = true
        try {
            const formData = { ...inputFields.value }

            const response = await createForloebsskabelon(formData)
            if(response !== null)
            {
                router.push({ path: 'forloeb-overview', query: { tid: response.data.uid } })
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
			<input type="text" id="duration" name="duration" placeholder=" " ref="varighed" v-model="inputFields.varighed" @input="varighed.value=varighed.value.replace(/(?![0-9])./gmi,'').slice(0, 2)" required>
			<label for="duration" class="floating-label">Forløbets varighed (dage)</label>
		</div>

		<div class="inputContainer submit">
			<button class="button button-outline" type="submit" :disabled="isSubmitting">+ Opret forløbsskabelon</button>
		</div>

	</div>
	</form>
</template>