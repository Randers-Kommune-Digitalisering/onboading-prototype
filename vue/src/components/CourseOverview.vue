<script setup>
    import { ref, onMounted } from 'vue'
    import { useRouter } from 'vue-router'
    
    import { getForloebByEmail, getForloebById, completeForloeb, deleteForloeb } from '@/services/forløbService.js'
    import { getForloebsskabelonById, deleteForloebsskabelon } from '@/services/forløbsskabelonService.js'
    import { getOpgaverByForloebID, getOpgaverByForloebsskabelonID, getOpgaverByAnsvarligEmail } from '@/services/opgaveService.js'
    import TaskList from '@/components/TaskList.vue'
    import CourseItem from '@/components/CourseItem.vue'
    import Placeholder from '@/components/Placeholder.vue'
    import ProgressBar from '@/components/ProgressBar.vue'

    const router = useRouter()

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
    const isForloebCompleted = ref(false)
    const isOpgaverFetched = ref(false)
    const opgaver_all = ref([])
    const completedPercentage = ref(0)
    const opgaver_ongoing = ref([])
    const opgaver_future = ref([])
    const opgaver_completed = ref([])
    const opgaver_template = ref([])

    const fetchOpgaver = async () => {
        try {
            const headers = { usermail: props.userEmail ?? props.ansvarligEmail }

            if (props.userEmail || props.ansvarligEmail || (props.id && props.adminView)) {
                const forloeb_response =  props.ansvarligEmail ? null
                                        : props.userEmail ? await getForloebByEmail({ headers }) 
                                        : props.isTemplate ? await getForloebsskabelonById(props.id, { headers })
                                        : await getForloebById(props.id, { headers })
                
                forloeb.value = forloeb_response?.data
                isForloebCompleted.value = forloeb.value?.enddate ? new Date(forloeb.value.enddate) <= new Date() : false

                forloeb_id.value = forloeb.value?.ForløbID || forloeb.value?.ForløbsskabelonID
                const opgaver_response =  props.ansvarligEmail ? await getOpgaverByAnsvarligEmail({ headers }) 
                                        : props.isTemplate ? await getOpgaverByForloebsskabelonID(forloeb_id.value)
                                        : await getOpgaverByForloebID(forloeb_id.value, { headers })

                if (opgaver_response?.data == null)
                {
                    console.log('No tasks found')
                    isOpgaverFetched.value = true
                    return
                }
                
                if (!Array.isArray(opgaver_response.data))
                    opgaver_response.data = [opgaver_response.data]

                // Sort and 
                // Store opgaver in different arrays based on their status
                if(props.isTemplate)
                    opgaver_response.data.sort((a, b) => a.relativ_startdag - b.relativ_startdag)
                else
                    opgaver_response.data.sort((a, b) => new Date(a.slutdato) - new Date(b.slutdato))

                opgaver_all.value = opgaver_response.data
                completedPercentage.value = opgaver_all.value.length > 0 ? Math.round(opgaver_all.value.filter(opgave => opgave.result).length / opgaver_all.value.length * 100) : 0

                if(props.isTemplate)
                    opgaver_template.value = opgaver_response.data
                else
                    for (const item of opgaver_response.data) {
                        if (item.result)
                            opgaver_completed.value.push(item)
                        else
                        if (new Date(item.startdato) > new Date())
                            opgaver_future.value.push(item)
                        else 
                            opgaver_ongoing.value.push(item)
                    }
                opgaver_future.value.sort((a, b) => new Date(a.startdato) - new Date(b.startdato))

                isOpgaverFetched.value = true

            } else {
                console.log('Please provide user email')
            }

        } catch (error) {
            console.log(error)
            isOpgaverFetched.value = true
        }
    }

    const completeCourse = () => {
        completeForloeb(forloeb_id.value).then(response => {
            const currentPath = { path: router.currentRoute.value.path, query: router.currentRoute.value.query }
            router.replace({ path: '/reload' }).then(() => {
                router.replace(currentPath)
            })
        }).catch(error => {
            console.error('Error completing course:', error)
        })
    }

    const deleteCourse = () => {
        if(!confirm(`Er du sikker på, at du vil slette ${props.isTemplate ? 'denne skabelon' : 'dette forløb'}?`))
            return

        if(props.isTemplate)
            deleteForloebsskabelon(forloeb_id.value).then(response => {
                router.replace({ path: '/template-overview' })
            }).catch(error => {
                console.error('Error deleting template:', error)
            })
        else
            deleteForloeb(forloeb_id.value).then(response => {
                router.replace({ path: '/admin-overview' })
            }).catch(error => {
                console.error('Error deleting course:', error)
            })
    }

    onMounted(() => {
        try {
            fetchOpgaver()
        } catch (error) {
            console.log(error)
        }
    })
</script>
<template>
    <p v-if="showDetails" class="indent-tiny bold uppercase p-header-adjust">Oversigt</p>
    <CourseItem v-if="forloeb != null && isOpgaverFetched && showDetails"
                :disableInteraction="true" 
                :dark="true" 
                :id="!isTemplate ? forloeb_id : null" 
                :tid="!isTemplate ? forloeb_id : null" 
                :title="forloeb.usermail || 'Skabelon'" 
                :name="forloeb.name" 
                :duration="forloeb.varighed" 
                :startDate="new Date(forloeb.startdate)" 
                :deadline="new Date(forloeb.enddate)"
                :tasks="opgaver_all" />
    <Placeholder v-if="!isOpgaverFetched && showDetails" :height="isTemplate ? 4.5 : 7.2" :dark="true" />
    <ProgressBar v-if="!showDetails && !ansvarligEmail" :percentage="completedPercentage"></ProgressBar>
    <div class="buttons" v-if="adminView">
        <router-link :to="`/create-opgave?id=${forloeb_id}`" class="button" v-if="!isTemplate && !isForloebCompleted">+ Tilføj opgave</router-link>
        <router-link :to="`/create-opgave?tid=${forloeb_id}`" class="button" v-if="isTemplate">+ Tilføj opgave</router-link>
        <router-link :to="`/create-forloeb${isTemplate ? 'sskabelon':''}?edit=true&id=${forloeb_id}`" class="button hollow">Redigér {{isForloebCompleted ? ' / genoptag ' : '' }}{{ isTemplate ? 'skabelon' : 'forløb' }}</router-link>
        <div @click="completeCourse()" class="button hollow red" v-if="!isTemplate && !isForloebCompleted">Afslut forløb</div>
        <div @click="deleteCourse()" class="button red hollow" v-if="isTemplate || isForloebCompleted">Slet {{ isTemplate ? 'skabelon' : 'forløb' }}</div>
        <router-link :to="`/create-forloeb?tid=${forloeb_id}`" class="button" v-if="isTemplate">+ Opret forløb med skabelon</router-link>
    </div>
    <TaskList v-if="forloeb != null && isTemplate" :tasks="opgaver_template" :adminView="adminView" title="Alle opgaver" :expandFirstItem="false" :templateView="true" />
    <TaskList v-if="(forloeb != null || ansvarligEmail != null) && !isTemplate" :tasks="opgaver_ongoing" :adminView="adminView || ansvarligEmail != null" :largeHeaderAdjust="(!showDetails && ansvarligEmail == null) || adminView" />
    <TaskList v-if="(forloeb != null || ansvarligEmail != null) && !isTemplate" :tasks="opgaver_future" :adminView="adminView || ansvarligEmail != null" title="Kommende opgaver" :largeHeaderAdjust="true" :expandFirstItem="false" itemColor="777371" />
    <TaskList v-if="(forloeb != null || ansvarligEmail != null) && !isTemplate" :tasks="opgaver_completed" :adminView="adminView || ansvarligEmail != null" title="Afsluttede opgaver" :largeHeaderAdjust="true" :expandFirstItem="false" :dark="true" itemColor="617a5d" />
</template>