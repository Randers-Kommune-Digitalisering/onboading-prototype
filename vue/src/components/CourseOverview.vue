<script setup>
    import { computed, ref, onMounted, watch } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
    import { getUserInfo } from '@/services/keycloakService.js'
    import { getExternalUserInfo } from '@/services/externalAccessService.js'
    
    import { getForloebByEmail, getForloebById, getForloebByIdExternal, completeForloeb, deleteForloeb } from '@/services/forløbService.js'
    import { getForloebsskabelonById, deleteForloebsskabelon } from '@/services/forløbsskabelonService.js'
    import { getOpgaverByForloebID, getOpgaverByForloebIDExternal, getOpgaverByForloebIDAdmin, getOpgaverByForloebsskabelonID, getOpgaverByAnsvarligEmail } from '@/services/opgaveService.js'
    import TaskList from '@/components/TaskList.vue'
    import CourseItem from '@/components/CourseItem.vue'
    import Placeholder from '@/components/Placeholder.vue'
    import ProgressBar from '@/components/ProgressBar.vue'

    const router = useRouter()
    const route = useRoute()

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
        scrollToItem: {
            type: Number,
            default: null
        },
        ansvarligView: {
            type: Boolean,
            default: false
        },
        external: {
            type: Boolean,
            default: false
        },
        accessKey: {
            type: String,
            default: null
        }
    })

    const forloeb = ref(null)
    const forloeb_id = ref(null)
    const userTitle = ref(null)
    const userInfo = ref({
        roles: [],
        email: '',
        isAdmin: false,
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
    const externalAccessDenied = ref(false)
    const roleAccessDenied = ref(false)

    const isNestedForloebRoute = (path) => path.startsWith('/forloeb-overview/')
    const isBaseForloebRoute = (path) => path === '/forloeb-overview' || path === '/forloeb-overview/'
    const showTaskLists = computed(() => !isNestedForloebRoute(route.path))

    const resetTaskState = () => {
        opgaver_all.value = []
        opgaver_ongoing.value = []
        opgaver_future.value = []
        opgaver_completed.value = []
        opgaver_template.value = []
        completedPercentage.value = 0
        start_message_index.value = -1
    }

    const getTaskId = (task) => task?.OpgaveID ?? task?.OpgaveskabelonID

    const removeTaskFromListById = (taskList, taskId) => {
        const index = taskList.findIndex(task => getTaskId(task) === taskId)
        if (index !== -1)
            taskList.splice(index, 1)
    }

    const getProgressTasks = (tasks) => (tasks || []).filter(opgave => opgave?.hidden !== true)

    const updateCompletedPercentage = () => {
        const progressTasks = getProgressTasks(opgaver_all.value)
        completedPercentage.value = progressTasks.length > 0
            ? Math.round(progressTasks.filter(opgave => opgave.result).length / progressTasks.length * 100)
            : 0
    }

    const handleTaskResultChange = ({ id, result }) => {
        const task = opgaver_all.value.find(item => getTaskId(item) === id)
        if (!task)
            return

        task.result = result
        updateCompletedPercentage()

        if (props.isTemplate || isUnderPreparation.value)
            return

        removeTaskFromListById(opgaver_ongoing.value, id)
        removeTaskFromListById(opgaver_future.value, id)
        removeTaskFromListById(opgaver_completed.value, id)

        if (result)
            opgaver_completed.value.push(task)
        else if (new Date(task.startdato) > new Date())
            opgaver_future.value.push(task)
        else
            opgaver_ongoing.value.push(task)

        opgaver_future.value.sort((a, b) => new Date(a.startdato) - new Date(b.startdato))
    }

    const fetchOpgaver = async () => {
        resetTaskState()
        isOpgaverFetched.value = false

        // External access flow
        try {
            if (props.external) {
                externalAccessDenied.value = false
                const externalInfoResponse = await getExternalUserInfo(props.id, props.accessKey)
                userInfo.value = {
                    roles: ['Public'],
                    email: externalInfoResponse?.data?.email || '',
                    isAdmin: false,
                    isMedarbejder: false,
                }

                const forloeb_response = await getForloebByIdExternal(props.id, props.accessKey)
                isForloebFetched.value = true
                forloeb.value = forloeb_response?.data

                if (forloeb_response && forloeb.value == null) {
                    isOpgaverFetched.value = true
                    return
                }

                isUnderPreparation.value = forloeb.value?.isPreparation || false
                isForloebCompleted.value = !isUnderPreparation.value && forloeb.value?.enddate ? new Date(forloeb.value.enddate) <= new Date() : false
                isForloebOngoing.value = !isUnderPreparation.value && forloeb.value?.startdate ? new Date(forloeb.value.startdate) <= new Date() : false
                forloeb_id.value = forloeb.value?.ForløbID
                userTitle.value = forloeb.value?.userdq != '' ? forloeb.value?.userdq : forloeb.value?.usermail

                if (forloeb.value?.opgave_grupper && Array.isArray(forloeb.value.opgave_grupper))
                {
                    forloeb.value?.opgave_grupper.sort((a, b) => a.name.localeCompare(b.name))
                    sortBy.value = 'gruppe'
                }

                const opgaver_response = await getOpgaverByForloebIDExternal(forloeb_id.value, props.accessKey)

                if (opgaver_response?.data == null) {
                    console.warn('No tasks found')
                    isOpgaverFetched.value = true
                    return
                }

                if (!Array.isArray(opgaver_response.data))
                    opgaver_response.data = [opgaver_response.data]

                if (isUnderPreparation.value)
                    opgaver_response.data.sort((a, b) => a.relativ_startdag - b.relativ_startdag)
                else
                    opgaver_response.data.sort((a, b) => new Date(a.slutdato) - new Date(b.slutdato))

                opgaver_all.value = opgaver_response.data
                updateCompletedPercentage()

                if (isUnderPreparation.value)
                {
                    opgaver_template.value = opgaver_response.data
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
                    opgaver_future.value.sort((a, b) => new Date(a.startdato) - new Date(b.startdato))
                    if (!isForloebOngoing.value && forloeb.value?.startdate)
                        start_message_index.value = opgaver_future.value
                            .map(opgave => new Date(opgave.startdato) > new Date(forloeb.value.startdate))
                            .findIndex(opgave => opgave)
                }

                isOpgaverFetched.value = true
                return
            }

            // Internal access flow (logged in AD users)
            if (userInfo.value) {
                roleAccessDenied.value = false
                const headers = { usermail: userInfo.value.email }
                // Get forloeb
                                        // In ansvarligView, fetch no forløb unless id is provided (fetch opgaver only)
                const forloeb_response =  props.ansvarligView && !props.id ? null
                                        // As medarbejder fetch forløb by email
                                        : userInfo.value.isMedarbejder && !props.id ? await getForloebByEmail({ headers })
                                        // If template fetch by skabelon id
                                        : props.isTemplate ? await getForloebsskabelonById(props.id)
                                        // Otherwise fetch by id and user email (for admins and ansvarlig users)
                                        : await getForloebById(props.id, { headers })
                isForloebFetched.value = true
                forloeb.value = forloeb_response?.data
                if (forloeb_response && forloeb.value == null) {
                    isOpgaverFetched.value = true
                    return
                }
                isUnderPreparation.value = forloeb.value?.isPreparation || false
                isForloebCompleted.value = !isUnderPreparation.value && forloeb.value?.enddate ? new Date(forloeb.value.enddate) <= new Date() : false
                isForloebOngoing.value = !isUnderPreparation.value && forloeb.value?.startdate ? new Date(forloeb.value.startdate) <= new Date() : false
                forloeb_id.value = forloeb.value?.ForløbID || forloeb.value?.ForløbsskabelonID
                userTitle.value = forloeb.value?.userdq != '' ? forloeb.value?.userdq : forloeb.value?.usermail
                if (forloeb.value?.opgave_grupper && Array.isArray(forloeb.value.opgave_grupper))
                {
                    forloeb.value?.opgave_grupper.sort((a, b) => a.name.localeCompare(b.name))
                    sortBy.value = 'gruppe'
                }
                
                // Get opgaver
                                        // In ansvarligView fetch opgaver
                const opgaver_response =  props.ansvarligView && !props.id ? await getOpgaverByAnsvarligEmail({ headers }) 
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
                updateCompletedPercentage()

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

            // If external access, show specific message if 403 Forbidden (likely expired or invalid link)
            if (props.external && error?.response?.status === 403)
                externalAccessDenied.value = true
            else if (error?.response?.status === 403)
                roleAccessDenied.value = true

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

    const returnToOverview = () => {
        const query = {
            sort: sortBy.value,
            refreshTasks: Date.now().toString(),
        }

        const currentQuery = router.currentRoute.value.query
        const isTemplateContext = props.isTemplate
            || currentQuery.template === 'true'
            || route.query.tid != null
            || route.query.forloebTid != null

        const parentForloebId = route.query.forloebTid || route.query.forloebId || route.query.tid || route.query.id || forloeb_id.value
        if (parentForloebId != null) {
            if (isTemplateContext)
                query.tid = parentForloebId
            else
                query.id = parentForloebId
        }

        // On task routes (e.g. create-opgave/edit), `id` is often the task id while
        // `forloebId` points to the parent forloeb. Preserve that task id for scroll/focus.
        query.item = currentQuery.item || ((currentQuery.forloebId != null || currentQuery.forloebTid != null) ? currentQuery.id : null)

        if (route.query.external != null)
            query.external = route.query.external

        router.replace({ path: '/forloeb-overview', query })
    }

    onMounted(async () => {
        try {
            if (!props.external)
                userInfo.value = await getUserInfo()
            await fetchOpgaver()
        } catch (error) {
            console.error(error)
        }
    })

    watch(() => route.query.refreshTasks, async (newValue, oldValue) => {
        if (newValue === oldValue)
            return

        if (!showTaskLists.value)
            return

        await fetchOpgaver()
    })

    watch(() => route.path, async (newPath, oldPath) => {
        if (!isBaseForloebRoute(newPath))
            return

        if (!isNestedForloebRoute(oldPath || ''))
            return

        await fetchOpgaver()
    })

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
    <p v-if="externalAccessDenied" class="indent-tiny notification">
        <span class="bold">OBS</span>: Linket er ugyldigt eller udløbet. <router-link :to="`/forloeb-overview?id=${props.id}&external=true&refresh=true`">Anmod om et nyt link</router-link>.
    </p>
    <p v-if="roleAccessDenied" class="indent-tiny notification">
        <span class="bold">OBS</span>: Du har ikke adgang til dette forløb.<br />Kontakt din leder eller administrator hvis du mener, at dette er en fejl.
    </p>
    <p v-if="forloeb == null && isForloebFetched && !props.ansvarligView && !externalAccessDenied && !roleAccessDenied" class="indent-tiny notification">
        <span class="bold">OBS</span>: Det ser ikke ud til, at du har et onboardingforløb tilknyttet.<br />Kontakt din leder eller administrator hvis du mener, at dette er en fejl.
    </p>
    <p v-if="forloeb != null && isForloebFetched && userInfo.isAdmin && isForloebOngoing && !forloeb.usermail.includes('@randers.dk')" class="indent-tiny notification yellow">
        <span class="bold">OBS</span>: Forløbet er oprettet med medarbejderens private mailadresse. Husk at opdatere til medarbejderens nye Randers-mail når medarbejderen er startet i kommunen.
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
    />

    <Placeholder v-if="!isOpgaverFetched && showDetails" :height="isTemplate || isUnderPreparation ? 4.5 : 7.2" :dark="true" />
    <ProgressBar v-if="forloeb != null  && !showDetails && !isUnderPreparation" :percentage="completedPercentage"></ProgressBar>
    
    <!-- Admin actions -->
    <div class="buttons" v-if="userInfo.isAdmin && !props.ansvarligView && forloeb != null && isOpgaverFetched">

        <div @click="returnToOverview()"
             class="button hollow"
             v-if="!showTaskLists">
                <i class="fa-solid fa-chevron-left" style="font-size: 0.6em;margin-right:0.4rem;transform:translateY(-0.06rem)"></i>
                Tilbage til oversigt
        </div>

        <template v-else>

        <router-link :to="`/forloeb-overview/create-opgave?id=${forloeb_id}&prep=${isUnderPreparation}`"
                     class="button" v-if="!isTemplate && !isForloebCompleted">
                        + Tilføj opgave
        </router-link>

        <router-link :to="`/forloeb-overview/create-opgave?tid=${forloeb_id}`"
                     class="button"
                     v-if="isTemplate">
                        + Tilføj opgave
        </router-link>

        <router-link :to="`/forloeb-overview/edit-forloeb?id=${forloeb_id}`" v-if="!isTemplate"
                     class="button hollow">
                        Redigér{{isForloebCompleted ? ' / genoptag' : '' }} forløb
        </router-link>

        <router-link :to="`/forloeb-overview/create-forloebsskabelon?tid=${forloeb_id}&edit=true`" v-else
                     class="button hollow">
                        Redigér skabelon
        </router-link>

        <router-link :to="`/forloeb-overview/send-velkomst?id=${forloeb_id}`"
             class="button hollow dashed"
             v-if="!isTemplate && !isUnderPreparation">
                Send velkomstmail
        </router-link>

        <div @click="completeCourse()"
             class="button hollow red"
             v-if="!isTemplate && isForloebOngoing && !isForloebCompleted">
                Afslut forløb
        </div>

        <router-link :to="`/forloeb-overview/start-forloeb?id=${forloeb_id}`"
                     class="button hollow yellow"
                     v-if="!isTemplate && isUnderPreparation">
                        Start forløb
        </router-link>

        <div @click="deleteCourse()"
             class="button red hollow"
             v-if="isTemplate || isForloebCompleted || (!isForloebCompleted && !isForloebOngoing)">
                Slet {{ isTemplate ? 'skabelon' : 'forløb' }}
        </div>

        </template>

    </div>

    <div v-if="showTaskLists && forloeb != null && forloeb?.opgave_grupper?.length > 0" class="sort-container">
        <div style="flex-grow:1">&nbsp;</div>
        <div class="sort-title">Sortér efter:</div>
        <select class="sort-selector" v-model="sortBy">
            <option value="gruppe">Gruppe</option>
            <option value="deadline">{{ isUnderPreparation || isTemplate ? 'Startdag' : 'Deadline' }}</option>
        </select>
    </div>
    <div :class="{ 'ansvarlig-view': props.ansvarligView }" v-if="showTaskLists && sortBy === 'deadline'">
        <TaskList v-if="forloeb != null && (isTemplate || isUnderPreparation)"
                :tasks="opgaver_template"
                :isFetchingTasks="!isOpgaverFetched"
                title="Alle opgaver"
                :largeHeaderAdjust="true"
                :scrollToItem="scrollToItem"
                :templateView="isTemplate"
                :isPreparation="isUnderPreparation"
                :external="props.external"
                :accessKey="props.accessKey"
                :forloebStartDate="new Date(forloeb?.startdate)"
                :startMessageIndex="start_message_index"
                @task-result-change="handleTaskResultChange" />

        <TaskList v-if="(forloeb != null || props.ansvarligView) && (!isTemplate && !isUnderPreparation)"
                :tasks="opgaver_ongoing"
                :isFetchingTasks="!isOpgaverFetched"
                :title="props.id != null ? 'Aktuelle opgaver' : 'Mine opgaver'"
                :largeHeaderAdjust="(!props.ansvarligView && id != null) || (!props.ansvarligView && !userInfo.isAdmin)"
                :scrollToItem="scrollToItem"
                :external="props.external"
                :accessKey="props.accessKey"
                @task-result-change="handleTaskResultChange" />

        <TaskList v-if="(forloeb != null || props.ansvarligView) && (!isTemplate && !isUnderPreparation)"
                :tasks="opgaver_future"
                :isFetchingTasks="!isOpgaverFetched"
                title="Kommende opgaver"
                :largeHeaderAdjust="true"
                :scrollToItem="scrollToItem"
                :external="props.external"
                :accessKey="props.accessKey"
                :forloebStartDate="new Date(forloeb?.startdate)"
                :startMessageIndex="start_message_index"
                @task-result-change="handleTaskResultChange" />

        <TaskList v-if="(forloeb != null || props.ansvarligView) && (!isTemplate && !isUnderPreparation)"
                :tasks="opgaver_completed"
                :isFetchingTasks="!isOpgaverFetched"
                title="Afsluttede opgaver"
                :largeHeaderAdjust="true"
                :scrollToItem="scrollToItem"
                :dark="true"
                :external="props.external"
                :accessKey="props.accessKey"
                itemColor="617a5d"
                @task-result-change="handleTaskResultChange" />
    </div>
    <div :class="{ 'ansvarlig-view': props.ansvarligView }" v-else-if="showTaskLists">
        <TaskList v-if="forloeb != null" v-for="group in forloeb.opgave_grupper" :key="group.id"
                :tasks="opgaver_all.filter(opgave => opgave.gruppe?.OpgaveGruppeID === group.OpgaveGruppeID)"
                :isFetchingTasks="!isOpgaverFetched"
                :title="group.name"
                :largeHeaderAdjust="true"
                :scrollToItem="scrollToItem"
                :templateView="isTemplate"
                :isPreparation="isUnderPreparation"
                :external="props.external"
                :accessKey="props.accessKey"
                @task-result-change="handleTaskResultChange" />

        <TaskList v-if="forloeb != null && (forloeb.opgave_grupper.length === 0 || opgaver_all.filter(opgave => opgave.gruppe?.OpgaveGruppeID == null).length > 0)"
                :tasks="opgaver_all.filter(opgave => opgave.gruppe?.OpgaveGruppeID == null)"
                :isFetchingTasks="!isOpgaverFetched"
                title="Ingen gruppe"
                :largeHeaderAdjust="true"
                :scrollToItem="scrollToItem"
                :templateView="isTemplate"
                :isPreparation="isUnderPreparation"
                :external="props.external"
                :accessKey="props.accessKey"
                @task-result-change="handleTaskResultChange" />
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