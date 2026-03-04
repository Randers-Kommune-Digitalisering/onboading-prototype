<script setup>
    import { ref, onMounted } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
	
    import { createRessource, getRessourceById, updateRessource, deleteRessource } from '@/services/ressourceService.js'

    const route = useRoute()
	const router = useRouter()

	const id = parseInt(route.query.id ?? route.query.tid, 10)
    const isTemplate = route.query.id == null
	const isEditing = route.query.edit == 'true'
	const opgaveId = ref(isEditing ? null : id)
    const isSubmitting = ref(false)
	const isUrlValid = ref(true)

	const inputFields = ref({
        name: "",
        url: ""
    })

	const addHttp = () => {
		if (!inputFields.value.url.startsWith('http://') && !inputFields.value.url.startsWith('https://')) {
			inputFields.value.url = 'https://' + inputFields.value.url
		}
		return url
	}

	const evaluateUrl = (url) => {
		const regex = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?.*$/
		isUrlValid.value = regex.test(url)
		return isUrlValid.value
	}

	/* Instantiate */

	onMounted(() => {
        if(!id) {
            console.error('No ID provided')
            router.back()
            return
        }
		if(isEditing) {
			getRessourceById(id).then(response => {
				inputFields.value.name = response.data.name
				inputFields.value.url = response.data.url
				opgaveId.value = response.data.OpgaveID ?? response.data.OpgaveskabelonID
			}).catch(error => {
				console.error('Error fetching ressource:', error)
			})
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
				inputFields.value.OpgaveskabelonID = id
			else if (!isEditing)
				inputFields.value.OpgaveID = id

            const formData = { ...inputFields.value }

            const response = isEditing ? await updateRessource(id, formData) : await createRessource(formData)
            if(response !== null)
				returnToPrevious()
            else
                console.error('Response:', response)

        } catch (error) {
            console.error('Error:', error.response?.data?.error ?? error)
        }
        isSubmitting.value = false
    }

	const deleteItem = () =>
	{
		console.warn('Deleting ressource:', id)
		deleteRessource(id)
		.then(response => {
			returnToPrevious()
		})
		.catch(error => {
			console.error('Error deleting ressource:', error)
		})
	}

	const returnToPrevious = () =>
	{
		// Get last route
		let lastUrl = router.options.history.state.back
		let lastRoute = router.getRoutes().find(route => route.path == lastUrl.split('?')[0])
		lastRoute.query = Object.fromEntries(new URLSearchParams(lastUrl.split('?')[1]))

		// Add query params
		lastRoute.query = { ...lastRoute.query, item: opgaveId.value }
		if (isTemplate)
			lastRoute.query.view = '1'

		// Go back
		router.replace({ path: lastRoute.path, query: lastRoute.query })
	}
	
</script>

<template>
	<p class="indent-tiny bold uppercase p-header-adjust">Tilføj ressource til opgaven</p>

	<form @submit.prevent="submitForm">
	<div class="formContainer">

		<div class="inputContainer">
			<input type="text" id="title" name="title" placeholder=" " v-model="inputFields.name" required>
			<label for="title" class="floating-label">Ressourcens navn</label>
		</div>

		<div class="inputContainer">
			<input type="text" id="url" name="url" placeholder=" " v-model="inputFields.url" :class="{'invalid': !isUrlValid}" @change="addHttp()" required>
			<label for="url" class="floating-label">Link til ressource</label>
		</div>

		<div class="inputContainer submit">
			<div v-if="isEditing" class="button hollow red" @click="deleteItem()">Slet ressource</div>
			<button class="button" type="submit" :disabled="isSubmitting">{{ isEditing ? 'Opdater' : '+ Tilføj' }} ressource</button>
		</div>

	</div>
	</form>
</template>