<script setup>
    import { ref, onMounted } from 'vue'
    import keycloak from '@/keycloak'
    import { getForloebByEmail } from '@/services/forløbService'
    import { getOpgaverByForloebID } from '@/services/opgaveService'
    import TaskList from '@/components/TaskList.vue'

    const props = defineProps({
        userEmail: {
            type: String,
            required: true
        }
    })

    const forloeb = ref(null)
    const forloeb_id = ref(null)
    const opgaver = ref([])

    const fetchOpgaver = async () => {
        try {
            const headers = { usermail: props.userEmail }

            if (props.userEmail) {
                const forloeb_response = await getForloebByEmail({ headers })
                forloeb.value = forloeb_response.data

                forloeb_id.value = forloeb.value.ForløbID
                const opgaver_response = await getOpgaverByForloebID(forloeb_id.value, { headers })
                opgaver.value = opgaver_response != null ? opgaver_response.data : null //response.data.map(opgave => ({ ...opgave, showDetails: false }))
                
                if (!Array.isArray(opgaver.value))
                    opgaver.value = [opgaver.value]

            } else {
                console.log('Please provide user email')
            }

        } catch (error) {
            console.log(error)
            opgaver.value = []
        }
    }

    onMounted(() => {
        try {
            if (keycloak.authenticated) {
                console.log('User email: ', props.userEmail)
                fetchOpgaver()
            }
        } catch (error) {
            console.log(error)
        }
    })
</script>
<template>
    <TaskList :tasks="opgaver" />
</template>