<script setup>
    import { ref, onMounted } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
	
	import { createRessource, createRessourceFile, getRessourceById, updateRessource, deleteRessource } from '@/services/ressourceService.js'

    const route = useRoute()
	const router = useRouter()

	const id = parseInt(route.query.id ?? route.query.tid, 10)
    const isTemplate = route.query.id == null
	const isEditing = route.query.edit == 'true'
	const opgaveId = ref(isEditing ? null : id)
    const isSubmitting = ref(false)
	const isUrlValid = ref(true)
	const resourceType = ref('link') // 'link' | 'file'
	const selectedFile = ref(null)

	const inputFields = ref({
        name: "",
        url: ""
    })

	const addHttp = () => {
		if (!inputFields.value.url)
			return inputFields.value.url
		if (!inputFields.value.url.startsWith('http://') && !inputFields.value.url.startsWith('https://')) {
			inputFields.value.url = 'https://' + inputFields.value.url
		}
		return inputFields.value.url
	}

	const setResourceType = (type) => {
		if (isEditing)
			return
		resourceType.value = type
		isUrlValid.value = true
		selectedFile.value = null
	}

	const onFileSelected = (event) => {
		const files = event?.target?.files
		selectedFile.value = files && files.length > 0 ? files[0] : null
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
				resourceType.value = response.data.isFile ? 'file' : 'link'
				opgaveId.value = response.data.OpgaveID ?? response.data.OpgaveskabelonID
			}).catch(error => {
				console.error('Error fetching ressource:', error)
			})
		}
    })

	/* Submit */

	const submitForm = async () =>
    {
		if (resourceType.value === 'link') {
			evaluateUrl(inputFields.value.url)
			if (!isUrlValid.value)
				return
		} else {
			isUrlValid.value = true
			if (!isEditing && !selectedFile.value)
				return
		}

        isSubmitting.value = true
        try {
			if (resourceType.value === 'file') {
				if (isEditing) {
					const response = await updateRessource(id, { name: inputFields.value.name })
					if(response !== null)
						returnToPrevious()
					else
						console.error('Response:', response)
				} else {
					const formData = new FormData()
					formData.append('name', inputFields.value.name)
					if (isTemplate)
						formData.append('OpgaveskabelonID', id)
					else
						formData.append('OpgaveID', id)
					formData.append('file', selectedFile.value)

					const response = await createRessourceFile(formData)
					if(response !== null)
						returnToPrevious()
					else
						console.error('Response:', response)
				}
			} else {
				if (isTemplate)
					inputFields.value.OpgaveskabelonID = id
				else if (!isEditing)
					inputFields.value.OpgaveID = id

				const payload = { ...inputFields.value }
				const response = isEditing ? await updateRessource(id, payload) : await createRessource(payload)
            if(response !== null)
				returnToPrevious()
            else
                console.error('Response:', response)
			}

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

		<div class="inputContainer inline">
			<span class="text">Ressourcetype:</span>
			<div class="buttonContainer merged">
				<div :class="['button', resourceType === 'link' ? '' : 'hollow']" @click="setResourceType('link')">Link</div>
				<div :class="['button', resourceType === 'file' ? '' : 'hollow']" @click="setResourceType('file')">Fil</div>
			</div>
		</div>

		<div class="inputContainer">
			<input type="text" id="title" name="title" placeholder=" " v-model="inputFields.name" required>
			<label for="title" class="floating-label">Ressourcens navn</label>
		</div>

		<div class="inputContainer" v-if="resourceType === 'link'">
			<input type="text" id="url" name="url" placeholder=" " v-model="inputFields.url" :class="{'invalid': !isUrlValid}" @change="addHttp()" required>
			<label for="url" class="floating-label">Link til ressource</label>
		</div>

		<div class="inputContainer" v-else>
			<input v-if="!isEditing" type="file" id="file" name="file" placeholder=" "
				accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt"
				@change="onFileSelected" required>
			<label v-if="!isEditing" for="file" class="floating-label">Upload fil</label>
		</div>

		<div class="inputContainer submit">
			<div v-if="isEditing" class="button hollow red" @click="deleteItem()">Slet ressource</div>
			<button class="button" type="submit" :disabled="isSubmitting">{{ isEditing ? 'Opdater' : '+ Tilføj' }} ressource</button>
		</div>

	</div>
	</form>
</template>

<style scoped>
	.buttonContainer.merged {
		gap: 0 !important;
	}
	.buttonContainer.merged .button:first-child {
		border-bottom-right-radius: 0;
		border-top-right-radius: 0;
		padding-left: 1.3rem;
	}
	.buttonContainer.merged .button:last-child {
		border-bottom-left-radius: 0;
		border-top-left-radius: 0;
		padding-right: 1.3rem;
	}
	.inputContainer.inline {
		align-items: center;
		gap: 1rem;
	}
	.inputContainer.inline .text {
		margin-left: 0.6rem;
		color: var(--color-text-faded)
	}
</style>