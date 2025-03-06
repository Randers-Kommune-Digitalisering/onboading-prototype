<script setup>
    import { ref, onMounted } from 'vue'
    import keycloak from '@/keycloak'
    import { getForloebByEmail, getForloebById } from '@/services/forløbService'
    import { getOpgaverByForloebID } from '@/services/opgaveService'
    import TaskList from '@/components/TaskList.vue'
    import CourseItem from '@/components/CourseItem.vue'
    import Placeholder from './Placeholder.vue'

    const props = defineProps({
        showDetails: {
            type: Boolean,
            required: false,
            default: false
        },
        userEmail: {
            type: String,
            required: false
        },
        id: {
            type: Number,
            required: false
        },
        adminView: {
            type: Boolean,
            required: false,
            default: false
        }
    })

    const forloeb = ref(null)
    const forloeb_id = ref(null)
    const opgaver = ref([])

    const fetchOpgaver = async () => {
        try {
            const headers = { usermail: props.userEmail }

            if (props.userEmail || props.id) {
                const forloeb_response = props.userEmail ? await getForloebByEmail({ headers }) : await getForloebById(props.id, { headers })
                forloeb.value = forloeb_response.data
                console.log('Forløb: ', forloeb.value)

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
                //console.log('User email: ', props.userEmail)
                fetchOpgaver()
            }
        } catch (error) {
            console.log(error)
        }
    })
</script>
<template>
    <p v-if="showDetails" class="indent-tiny bold uppercase p-header-adjust">Oversigt</p>
    <CourseItem v-if="forloeb != null && showDetails" :disableInteraction="true" :dark="true" :id="forloeb_id" :title="forloeb.userdq" :name="forloeb.name" :startDate="new Date(forloeb.startdate)" :deadline="new Date(forloeb.enddate)" />
    <Placeholder v-if="forloeb == null && showDetails" :dark="true" />
    <div class="buttons" v-if="adminView">
        <router-link :to="`/create-opgave?id=${forloeb_id}`" class="button">+ Tilføj opgave</router-link>
        <router-link to="/" class="button disabled">Redigér forløb</router-link>
        <router-link to="/" class="button red disabled">Afslut forløb</router-link>
    </div>
    <TaskList v-if="forloeb != null" :tasks="opgaver" :adminView="adminView" />
</template>