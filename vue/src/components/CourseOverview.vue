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
            default: false
        },
        userInfo: {
            type: Object,
            required: true
        },
        userEmail: {
            type: String
        },
        ansvarligEmail: {
            type: String
        },
        id: {
            type: Number
        },
        isTemplate: {
            type: Boolean,
            default: false
        },
        expandItem: {
            type: Number,
            default: null
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
            if (props.userInfo) {
                const headers = { usermail: props.userInfo.email }
                // Get forloeb
                                        // As ansvarlig fetch no forløb unless id is provided (fetch opgaver only)
                const forloeb_response =  props.userInfo.isAnsvarlig && !props.id ? null
                                        // As medarbejder fetch forløb by email
                                        : props.userInfo.isMedarbejder ? await getForloebByEmail({ headers })
                                        // If template fetch by skabelon id
                                        : props.isTemplate ? await getForloebsskabelonById(props.id)
                                        // Otherwise fetch by id and user email (for admins and ansvarlig users)
                                        : await getForloebById(props.id, { headers })
                
                forloeb.value = forloeb_response?.data
                isForloebCompleted.value = forloeb.value?.enddate ? new Date(forloeb.value.enddate) <= new Date() : false
                forloeb_id.value = forloeb.value?.ForløbID || forloeb.value?.ForløbsskabelonID

                // Get opgaver
                                        // As ansvarlig fetch opgaver
                const opgaver_response =  props.userInfo.isAnsvarlig && !props.id ? await getOpgaverByAnsvarligEmail({ headers }) 
                                        // If template fetch by skabelon id
                                        : props.isTemplate ? await getOpgaverByForloebsskabelonID(forloeb_id.value)
                                        // Otherwise fetch by forløb id and user email (for medarbejder users, admins and ansvarlig users)
                                        : await getOpgaverByForloebID(forloeb_id.value)

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
                console.log('No user info provided')
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

    const downloadForloeb = async () => {
        try {
            // Wait for the server to generate the PDF
            const response = await fetch(`api/forloeb-download?id=${forloeb_id.value}`)
            if (!response.ok) {
                throw new Error('Failed to download file')
            }

            // Ensure the response is a valid PDF
            const blob = await response.blob();
            if (blob.type !== 'application/pdf') {
                throw new Error('Invalid PDF file')
            }

            // Create a download link and trigger the download
            const downloadLink = document.createElement('a')
            downloadLink.href = URL.createObjectURL(blob)
            downloadLink.download = `${forloeb.value.name}.pdf`
            document.body.appendChild(downloadLink)
            downloadLink.click()
            document.body.removeChild(downloadLink)
        } catch (error) {
            console.error('Error downloading file:', error)
        }
    }
</script>
<template>
    <p v-if="showDetails" class="indent-tiny bold uppercase p-header-adjust">
        Oversigt
    </p>
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
    <ProgressBar v-if="forloeb != null  && !showDetails" :percentage="completedPercentage"></ProgressBar>
    
    <!-- Admin actions -->
    <div class="buttons" v-if="userInfo.isAdmin">

        <router-link :to="`/create-opgave?id=${forloeb_id}`"
                     class="button" v-if="!isTemplate && !isForloebCompleted">
                        + Tilføj opgave
        </router-link>

        <router-link :to="`/create-opgave?tid=${forloeb_id}`"
                     class="button"
                     v-if="isTemplate">
                        + Tilføj opgave
        </router-link>

        <router-link :to="`/create-forloeb${isTemplate ? 'sskabelon':''}?edit=true&id=${forloeb_id}`"
                     class="button hollow">
                        Redigér {{isForloebCompleted ? ' / genoptag ' : '' }}{{ isTemplate ? 'skabelon' : 'forløb' }}
        </router-link>

        <div @click="downloadForloeb()"
             class="button hollow dashed"
             v-if="!isTemplate">
                Download PDF
        </div>

        <div @click="completeCourse()"
             class="button hollow red"
             v-if="!isTemplate && !isForloebCompleted">
                Afslut forløb
        </div>

        <div @click="deleteCourse()"
             class="button red hollow"
             v-if="isTemplate || isForloebCompleted">
                Slet {{ isTemplate ? 'skabelon' : 'forløb' }}
        </div>

        <router-link :to="`/create-forloeb?tid=${forloeb_id}`"
                     class="button"
                     v-if="isTemplate">
                        + Opret forløb med skabelon
        </router-link>

    </div>

    <TaskList v-if="forloeb != null && isTemplate"
              :tasks="opgaver_template"
              :isFetchingTasks="!isOpgaverFetched"
              :userInfo="userInfo"
              title="Alle opgaver"
              :expandFirstItem="false"
              :expandItem="expandItem"
              :templateView="true" />

    <TaskList v-if="(forloeb != null || userInfo.isAnsvarlig) && !isTemplate"
              :tasks="opgaver_ongoing"
              :isFetchingTasks="!isOpgaverFetched"
              :userInfo="userInfo"
              :title="!userInfo.isMedarbejder && id != null ? 'Aktuelle opgaver' : 'Dine opgaver'"
              :largeHeaderAdjust="userInfo.isAdmin || id != null"
              :expandFirstItem="false"
              :expandItem="expandItem" />

    <TaskList v-if="(forloeb != null || userInfo.isAnsvarlig) && !isTemplate"
              :tasks="opgaver_future"
              :isFetchingTasks="!isOpgaverFetched"
              :userInfo="userInfo"
              title="Kommende opgaver"
              :largeHeaderAdjust="true"
              :expandFirstItem="false"
              :expandItem="expandItem"
              itemColor="777371" />

    <TaskList v-if="(forloeb != null || userInfo.isAnsvarlig) && !isTemplate"
              :tasks="opgaver_completed"
              :isFetchingTasks="!isOpgaverFetched"
              :userInfo="userInfo"
              title="Afsluttede opgaver"
              :largeHeaderAdjust="true"
              :expandFirstItem="false"
              :expandItem="expandItem"
              :dark="true"
              itemColor="617a5d" />
</template>