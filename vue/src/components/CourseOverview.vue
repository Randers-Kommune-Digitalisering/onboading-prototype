<script setup>
    import { ref, onMounted } from 'vue'
    import keycloak from '@/keycloak'
    import { getForloebByEmail, getForloebById } from '@/services/forløbService'
    import { getOpgaverByForloebID, getOpgaverByAnsvarligEmail } from '@/services/opgaveService'
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
        ansvarligEmail: {
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
        },
        isTemplate: {
            type: Boolean,
            required: false,
            default: false
        }
    })

    const forloeb = ref(null)
    const forloeb_id = ref(null)
    const opgaver_ongoing = ref([])
    const opgaver_future = ref([])
    const opgaver_completed = ref([])

    const fetchOpgaver = async () => {
        try {
            const headers = { usermail: props.userEmail }

            if (props.userEmail || props.id) {
                const forloeb_response = props.ansvarligEmail ? null : props.userEmail ? await getForloebByEmail({ headers }) : await getForloebById(props.id, { headers })
                forloeb.value = forloeb_response.data
                
                console.log('Forløb: ', forloeb.value)

                forloeb_id.value = forloeb.value.ForløbID
                const opgaver_response = props.ansvarligEmail ? await getOpgaverByAnsvarligEmail({ headers }) : await getOpgaverByForloebID(forloeb_id.value, { headers })

                if (opgaver_response.data == null)
                    return
                
                if (!Array.isArray(opgaver_response.data))
                    opgaver_response.data = [opgaver_response.data]

                console.log('Opgaver: ', opgaver_response.data)

                for (const item of opgaver_response.data) {
                    console.log('Startdate: ', new Date(item.startdato))
                    console.log('Enddate: ', new Date(item.slutdato))
                    console.log('Current date: ', new Date())

                    if (new Date(item.startdato) > new Date())
                        opgaver_future.value.push(item)
                    else
                    if (new Date(item.slutdato) < new Date())
                        opgaver_completed.value.push(item)
                    else 
                        opgaver_ongoing.value.push(item)
                }

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
        <router-link :to="`/create-opgave?id=${forloeb_id}`" class="button" v-if="!isTemplate">+ Tilføj opgave</router-link>
        <router-link :to="`/create-opgave?tid=${forloeb_id}`" class="button" v-if="isTemplate">+ Tilføj opgave</router-link>
        <router-link to="/" class="button disabled">Redigér {{ isTemplate ? 'forløb' : 'skabelon' }}</router-link>
        <router-link to="/" class="button red disabled" v-if="!isTemplate">Afslut forløb</router-link>
        <router-link to="/" class="button red disabled" v-if="isTemplate">Slet skabelon</router-link>
    </div>
    <TaskList v-if="forloeb != null" :tasks="opgaver_ongoing" :adminView="adminView" />
    <TaskList v-if="forloeb != null" :tasks="opgaver_future" :adminView="adminView" title="Kommende opgaver" :largeHeaderAdjust="true" :expandFirstItem="false" />
    <TaskList v-if="forloeb != null" :tasks="opgaver_completed" :adminView="adminView" title="Afsluttede opgaver" :largeHeaderAdjust="true" :expandFirstItem="false" :dark="true" />
</template>