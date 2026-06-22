<script setup>
    import { ref, onMounted } from 'vue'
    import { useRouter, useRoute } from 'vue-router'
	
    import { createForloebsskabelon, getForloebsskabelonById, updateForloebsskabelon } from '@/services/forløbsskabelonService.js'

    const route = useRoute()
	const router = useRouter()

    const isSubmitting = ref(false)
    const isEditing = route.query.edit === 'true'
    const skabelon_id = isEditing ? parseInt(route.query.tid ?? route.query.id, 10) : null

	const inputFields = ref({
        name: "",
        varighed: 7
    })
    const varighed = ref(null)
    const durationAtOne = ref(false)

    const focusedInput = ref(null)
    const inputFieldDescriptions = ref({
        name: { text: "Forløbsskabelonens navn", tooltip: "<span>Giv skabelonen et beskrivende navn.</span><span>Navnet bruges, når du senere vælger en skabelon ved oprettelse af et forløb.</span>" },
        varighed: { text: "Forløbets varighed", tooltip: "<span>Angiv hvor mange dage forløbet skal vare.</span><span>Varigheden bruges til at bestemme udgangspunktet for hvornår forløbet afsluttes.</span>" }
    })

    /* Instantiate */
    onMounted(() => {
        if (isEditing) {
            getForloebsskabelonById(skabelon_id).then(response => {
                Object.assign(inputFields.value, response.data)
            }).catch(error => {
                console.error('Error fetching forløbsskabelon:', error)
            })
        }
    })

	/* Submit */

	const submitForm = async () =>
    {
        isSubmitting.value = true
        try {
            const formData = { ...inputFields.value }

            const response = isEditing ? await updateForloebsskabelon(skabelon_id, formData) : await createForloebsskabelon(formData)
            if(response !== null)
            {
                router.push({ path: '/forloeb-overview', query: { tid: response.data.uid } })
            }
            else
                console.error('Response:', response)

        } catch (error) {            
            console.error('Error:', error.response?.data?.error ?? error)
        }
        isSubmitting.value = false
    }

    const returnDagOrDage = (days) => {
        return days > 1 || days == 0 ? 'dage' : 'dag'
    }

</script>

<template>
    <div class="flex"><div class="max-width"><!-- wrapper -->

	<p class="indent-tiny bold uppercase p-header-adjust">{{ isEditing ? 'Rediger forløbsskabelon' : 'Opret forløbsskabelon' }}</p>

    <div
        v-if="focusedInput"
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
            <input type="text" id="title" name="title" placeholder=" " v-model="inputFields.name" required
                @focus="focusedInput = inputFieldDescriptions.name"
                @blur="focusedInput = null">
			<label for="title" class="floating-label">Forløbsskabelonens navn</label>
		</div>

		<div class="inputContainer">
			<input type="text" id="duration" name="duration" placeholder=" " class="padding-input" ref="varighed" v-model="inputFields.varighed" @input="varighed.value=varighed.value.replace(/(?![0-9])./gmi,'').slice(0, 3)" required
				@focus="focusedInput = inputFieldDescriptions.varighed"
				@blur="focusedInput = null">
			<label for="duration" class="floating-label">Forløbets varighed</label>
            <label for="duration" class="annot-label">{{ returnDagOrDage(inputFields.varighed) }}</label>
            <div :class="['floating-button', 'indent-floating-button', { 'disabled': durationAtOne}]"
                    @click="inputFields.varighed--;durationAtOne = inputFields.varighed==1">
                    <i class="fa fa-minus"></i>
                </div>
            <div class="floating-button" @click="durationAtOne = false;inputFields.varighed++">
                <i class="fa fa-plus"></i>
            </div>
		</div>

		<div class="inputContainer submit">
			<button class="button" type="submit" :disabled="isSubmitting">{{ isEditing ? 'Opdater forløbsskabelon' : '+ Opret forløbsskabelon' }}</button>
		</div>

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
</style>