<script setup>
    import { ref, onMounted } from 'vue'
    import { useRouter } from 'vue-router'
	
    import { createForloebsskabelon } from '@/services/forløbsskabelonService'

	const router = useRouter()

    const isSubmitting = ref(false)

	const inputFields = ref({
        name: "",
        varighed: 7
    })
    const varighed = ref(null)
    const durationAtOne = ref(false)

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

    const returnDagOrDage = (days) => {
        return days > 1 || days == 0 ? 'dage' : 'dag'
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
			<input type="text" id="duration" name="duration" placeholder=" " class="padding-input" ref="varighed" v-model="inputFields.varighed" @input="varighed.value=varighed.value.replace(/(?![0-9])./gmi,'').slice(0, 2)" required>
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
			<button class="button button-outline" type="submit" :disabled="isSubmitting">+ Opret forløbsskabelon</button>
		</div>

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
        padding-left: calc(45% - 2rem);
    }
</style>