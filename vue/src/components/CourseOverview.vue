<script setup>
    import { ref, onMounted, watch } from 'vue'
    import { useRouter } from 'vue-router'
    import { getUserInfo } from '@/services/keycloakService.js'
    
    import { getForloebByEmail, getForloebById, completeForloeb, deleteForloeb } from '@/services/forløbService.js'
    import { getForloebsskabelonById, deleteForloebsskabelon } from '@/services/forløbsskabelonService.js'
    import { getOpgaverByForloebID, getOpgaverByForloebIDAdmin, getOpgaverByForloebsskabelonID, getOpgaverByAnsvarligEmail } from '@/services/opgaveService.js'
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
        },
        ansvarligView: {
            type: Boolean,
            default: false
        }
    })

    const forloeb = ref(null)
    const forloeb_id = ref(null)
    const userTitle = ref(null)
    const userInfo = ref({
        roles: [],
        email: '',
        isAdmin: false,
        isAnsvarlig: false,
        isMedarbejder: false,
    })
    const isForloebCompleted = ref(false)
    const isForloebOngoing = ref(false)
    const isForloebFetched = ref(false)
    const isOpgaverFetched = ref(false)
    const isUnderPreparation = ref(false)
    const opgaver_all = ref([])
    const completedPercentage = ref(0)
    const opgaver_ongoing = ref([])
    const opgaver_future = ref([])
    const opgaver_completed = ref([])
    const opgaver_template = ref([])
    const sortBy = ref(router.currentRoute.value.query.sort || 'deadline')
    const start_message_index = ref(-1)

    const fetchOpgaver = async () => {
        try {
            if (userInfo.value) {
                const headers = { usermail: userInfo.value.email }
                // Get forloeb
                                        // As ansvarlig fetch no forløb unless id is provided (fetch opgaver only)
                const forloeb_response =  userInfo.value.isAnsvarlig && !props.id && props.ansvarligView ? null
                                        // As medarbejder fetch forløb by email
                                        : userInfo.value.isMedarbejder && !props.id ? await getForloebByEmail({ headers })
                                        // If template fetch by skabelon id
                                        : props.isTemplate ? await getForloebsskabelonById(props.id)
                                        // Otherwise fetch by id and user email (for admins and ansvarlig users)
                                        : await getForloebById(props.id, { headers })
                isForloebFetched.value = true
                forloeb.value = forloeb_response?.data
                isUnderPreparation.value = forloeb.value?.isPreparation || false
                isForloebCompleted.value = !isUnderPreparation.value && forloeb.value?.enddate ? new Date(forloeb.value.enddate) <= new Date() : false
                isForloebOngoing.value = !isUnderPreparation.value && forloeb.value?.startdate ? new Date(forloeb.value.startdate) <= new Date() : false
                forloeb_id.value = forloeb.value?.ForløbID || forloeb.value?.ForløbsskabelonID
                userTitle.value = forloeb.value?.userdq != '' ? forloeb.value?.userdq : forloeb.value?.usermail
                if (forloeb.value?.opgave_grupper && Array.isArray(forloeb.value.opgave_grupper))
                    forloeb.value?.opgave_grupper.sort((a, b) => a.name.localeCompare(b.name))
                
                // Get opgaver
                                        // As ansvarlig fetch opgaver
                const opgaver_response =  userInfo.value.isAnsvarlig && !props.id && props.ansvarligView ? await getOpgaverByAnsvarligEmail({ headers }) 
                                        // If template fetch by skabelon id
                                        : props.isTemplate ? await getOpgaverByForloebsskabelonID(forloeb_id.value)
                                        // Otherwise fetch by forløb id and user email (for medarbejder users, admins and ansvarlig users)
                                        : userInfo.value.isAdmin ? await getOpgaverByForloebIDAdmin(forloeb_id.value)
                                        : await getOpgaverByForloebID(forloeb_id.value)

                if (opgaver_response?.data == null)
                {
                    console.warn('No tasks found')
                    isOpgaverFetched.value = true
                    return
                }
                
                if (!Array.isArray(opgaver_response.data))
                    opgaver_response.data = [opgaver_response.data]

                // Sort and 
                // Store opgaver in different arrays based on their status
                if(props.isTemplate || isUnderPreparation.value)
                    opgaver_response.data.sort((a, b) => a.relativ_startdag - b.relativ_startdag)
                else
                    opgaver_response.data.sort((a, b) => new Date(a.slutdato) - new Date(b.slutdato))

                opgaver_all.value = opgaver_response.data
                completedPercentage.value = opgaver_all.value.length > 0 ? Math.round(opgaver_all.value.filter(opgave => opgave.result).length / opgaver_all.value.length * 100) : 0

                if(props.isTemplate || isUnderPreparation.value)
                {
                    opgaver_template.value = opgaver_response.data
                    // Get first index of all tasks that start after forløb start date
                    start_message_index.value = opgaver_template.value
                        .map(opgave => opgave.relativ_startdag > -1)
                        .findIndex(opgave => opgave)
                }
                else
                {
                    for (const item of opgaver_response.data) {
                        if (item.result)
                            opgaver_completed.value.push(item)
                        else
                        if (new Date(item.startdato) > new Date())
                            opgaver_future.value.push(item)
                        else 
                            opgaver_ongoing.value.push(item)
                    }
                    // Get first index of future tasks that start after forløb start date
                    opgaver_future.value.sort((a, b) => new Date(a.startdato) - new Date(b.startdato))
                    if (!isForloebOngoing.value && forloeb.value?.startdate)
                        start_message_index.value = opgaver_future.value
                            .map(opgave => new Date(opgave.startdato) > new Date(forloeb.value.startdate))
                            .findIndex(opgave => opgave)
                }

                isOpgaverFetched.value = true

            } else {
                console.warn('No user info provided')
            }

        } catch (error) {
            console.error(error)
            isForloebFetched.value = true
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

    onMounted(async () => {
        try {
            userInfo.value = await getUserInfo()
            await fetchOpgaver()
        } catch (error) {
            console.error(error)
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

    watch(() => sortBy.value, (newSortingValue) => {
        router.replace({
            query: {
                ...router.currentRoute.value.query,
                sort: newSortingValue
            }
        })
    })
</script>
<template>
    <p v-if="forloeb == null && isForloebFetched && !props.ansvarligView" class="indent-tiny notification">
        <span class="bold">OBS</span>: Det ser ikke ud til, at du har et onboardingforløb tilknyttet.<br />Kontakt din leder eller administrator hvis du mener, at dette er en fejl.
    </p>
    <p v-if="forloeb != null && isForloebFetched && userInfo.isAdmin && isForloebOngoing && !forloeb.usermail.includes('@randers.dk')" class="indent-tiny notification yellow">
        <span class="bold">OBS</span>: Forløbet er oprettet med medarbejderens private mailadresse. Husk at opdatere til medarbejderens nye Randers-mail, så onboardingforløbet kan tilgås.
    </p>
    <p v-if="showDetails" class="indent-tiny bold uppercase p-header-adjust">
        Oversigt
    </p>
    <CourseItem v-if="forloeb != null && isOpgaverFetched && showDetails"
                :disableInteraction="true" 
                :dark="true" 
                :id="!isTemplate ? forloeb_id : null" 
                :tid="!isTemplate ? forloeb_id : null" 
                :title="userTitle" 
                :name="forloeb.name" 
                :duration="forloeb.varighed" 
                :startDate="new Date(forloeb.startdate)" 
                :deadline="new Date(forloeb.enddate)"
                :tasks="opgaver_all"
                :isPreparation="isUnderPreparation"
                :mails="forloeb.pending_emails" />

    <Placeholder v-if="!isOpgaverFetched && showDetails" :height="isTemplate || isUnderPreparation ? 4.5 : 7.2" :dark="true" />
    <ProgressBar v-if="forloeb != null  && !showDetails && !isUnderPreparation" :percentage="completedPercentage"></ProgressBar>
    
    <!-- Admin actions -->
    <div class="buttons" v-if="userInfo.isAdmin && !props.ansvarligView && forloeb != null && isOpgaverFetched">

        <router-link :to="`/create-opgave?id=${forloeb_id}&prep=${isUnderPreparation}`"
                     class="button" v-if="!isTemplate && !isForloebCompleted">
                        + Tilføj opgave
        </router-link>

        <router-link :to="`/create-opgave?tid=${forloeb_id}`"
                     class="button"
                     v-if="isTemplate">
                        + Tilføj opgave
        </router-link>

        <router-link :to="`/edit-forloeb?id=${forloeb_id}`" v-if="!isTemplate"
                     class="button hollow">
                        Redigér{{isForloebCompleted ? ' / genoptag' : '' }} forløb
        </router-link>

        <router-link :to="`/create-forloebsskabelon?id=${forloeb_id}&edit=true`" v-else
                     class="button hollow">
                        Redigér skabelon
        </router-link>

        <div @click="downloadForloeb()"
             class="button hollow dashed"
             v-if="!isTemplate && !isUnderPreparation">
                Download PDF
        </div>

        <div @click="completeCourse()"
             class="button hollow red"
             v-if="!isTemplate && isForloebOngoing && !isForloebCompleted">
                Afslut forløb
        </div>

        <router-link :to="`/start-forloeb?id=${forloeb_id}`"
                     class="button hollow yellow"
                     v-if="!isTemplate && isUnderPreparation">
                        Start forløb
        </router-link>

        <div @click="deleteCourse()"
             class="button red hollow"
             v-if="isTemplate || isForloebCompleted || (!isForloebCompleted && !isForloebOngoing)">
                Slet {{ isTemplate ? 'skabelon' : 'forløb' }}
        </div>

        <!-- <router-link :to="`/create-forloeb?tid=${forloeb_id}`"
                     class="button"
                     v-if="isTemplate">
                        + Opret forløb med skabelon
        </router-link> -->

    </div>

    <div v-if="forloeb != null && forloeb?.opgave_grupper?.length > 0" class="sort-container">
        <div style="flex-grow:1">&nbsp;</div>
        <div class="sort-title">Sortér efter:</div>
        <select class="sort-selector" v-model="sortBy">
            <option value="deadline">{{ isUnderPreparation || isTemplate ? 'Startdag' : 'Deadline' }}</option>
            <option value="gruppe">Gruppe</option>
        </select>
    </div>
    <div v-if="sortBy === 'deadline'">
        <TaskList v-if="forloeb != null && (isTemplate || isUnderPreparation)"
                :tasks="opgaver_template"
                :isFetchingTasks="!isOpgaverFetched"
                title="Alle opgaver"
                :largeHeaderAdjust="true"
                :expandFirstItem="false"
                :expandItem="expandItem"
                :templateView="isTemplate"
                :isPreparation="isUnderPreparation"
                :forloebStartDate="new Date(forloeb?.startdate)"
                :startMessageIndex="start_message_index" />

        <TaskList v-if="(forloeb != null || userInfo.isAnsvarlig) && (!isTemplate && !isUnderPreparation)"
                :tasks="opgaver_ongoing"
                :isFetchingTasks="!isOpgaverFetched"
                :title="props.id != null ? 'Aktuelle opgaver' : 'Mine opgaver'"
                :largeHeaderAdjust="(!props.ansvarligView && id != null) || (!props.ansvarligView && !userInfo.isAdmin)"
                :expandFirstItem="false"
                :expandItem="expandItem" />

        <TaskList v-if="(forloeb != null || userInfo.isAnsvarlig) && (!isTemplate && !isUnderPreparation)"
                :tasks="opgaver_future"
                :isFetchingTasks="!isOpgaverFetched"
                title="Kommende opgaver"
                :largeHeaderAdjust="true"
                :expandFirstItem="false"
                :expandItem="expandItem"
                itemColor="777371"
                :forloebStartDate="new Date(forloeb?.startdate)"
                :startMessageIndex="start_message_index" />

        <TaskList v-if="(forloeb != null || userInfo.isAnsvarlig) && (!isTemplate && !isUnderPreparation)"
                :tasks="opgaver_completed"
                :isFetchingTasks="!isOpgaverFetched"
                title="Afsluttede opgaver"
                :largeHeaderAdjust="true"
                :expandFirstItem="false"
                :expandItem="expandItem"
                :dark="true"
                itemColor="617a5d" />
    </div>
    <div v-else>
        <TaskList v-if="forloeb != null" v-for="group in forloeb.opgave_grupper" :key="group.id"
                :tasks="opgaver_all.filter(opgave => opgave.gruppe?.OpgaveGruppeID === group.OpgaveGruppeID)"
                :isFetchingTasks="!isOpgaverFetched"
                :title="group.name"
                :largeHeaderAdjust="true"
                :expandFirstItem="false"
                :expandItem="expandItem"
                :templateView="isTemplate"
                :isPreparation="isUnderPreparation" />

        
        <TaskList v-if="forloeb != null"
                :tasks="opgaver_all.filter(opgave => opgave.gruppe?.OpgaveGruppeID == null)"
                :isFetchingTasks="!isOpgaverFetched"
                title="Ingen gruppe"
                :largeHeaderAdjust="true"
                :expandFirstItem="false"
                :expandItem="expandItem"
                :templateView="isTemplate"
                :isPreparation="isUnderPreparation" />
    </div>

</template>

<style scoped>
    .sort-container {
        width: 100%;

        margin-right: 0.2rem;
        transform: translateY(1.1rem);
        float:left;

        display: flex;
        align-items: flex-end;
        gap: 0.6rem;
        font-size: 0.75em;
        text-transform: uppercase;
    }
    @media only screen and (min-width: 768px) {
        .sort-container {
            transform: translateY(1.7rem);
        }
    }
    .sort-container > .sort-title {
        font-weight: bold;
    }
    .sort-container > .sort-selector {
        padding: 0.3rem 0.6rem;
        background-color: var(--color-card-faded);
        cursor: pointer;
        width: auto;
        transform: translateY(0.3rem);
    }
</style>