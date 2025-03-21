<script setup>
    import { ref, onMounted } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
	
    import { createRessource, getRessourceById, updateRessource, deleteRessource } from '@/services/ressourceService'

    const route = useRoute()
	const router = useRouter()

	const opgave_id = parseInt(route.query.id ?? route.query.tid, 10)
    const isTemplate = route.query.id == null
	const isEditing = route.query.edit == 'true'
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
        if(!opgave_id) {
            console.error('No ID provided')
            router.back()
            return
        }
		console.log('Editing:', isEditing)
		if(isEditing) {
			getRessourceById(opgave_id).then(response => {
				console.log('Ressource response:', response)
				inputFields.value.name = response.data.name
				inputFields.value.url = response.data.url
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
				inputFields.value.OpgaveskabelonID = opgave_id
			else if (!isEditing)
				inputFields.value.OpgaveID = opgave_id

            const formData = { ...inputFields.value }

            const response = isEditing ? await updateRessource(opgave_id, formData) : await createRessource(formData)
            if(response !== null)
            {
                if (router.getRoutes()[router.getRoutes().length-1].name == "ForløbOverview")
                    router.back()
				else if (router.getRoutes()[router.getRoutes().length-1].name == "Reload")
					router.back(2)
            }
            else
                console.log('Response:', response)

        } catch (error) {
            console.log('Error:', error.response?.data?.error ?? error)
        }
        isSubmitting.value = false
    }

	const deleteItem = () =>
	{
		console.log('Deleting ressource:', opgave_id)
		deleteRessource(opgave_id)
		.then(response => {
			if (router.getRoutes()[router.getRoutes().length-1].name == "ForløbOverview")
				router.back()
			else if (router.getRoutes()[router.getRoutes().length-1].name == "Reload")
				router.back(2)
		})
		.catch(error => {
			console.error('Error deleting ressource:', error)
		})
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
			<button class="button button-outline" type="submit" :disabled="isSubmitting">{{ isEditing ? 'Opdater' : '+ Tilføj' }} ressource</button>
		</div>

	</div>
	</form>
</template>