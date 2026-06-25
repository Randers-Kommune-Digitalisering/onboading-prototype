<script setup>
    import { ref, onMounted, watch } from 'vue'
    import { useRouter } from 'vue-router'

    import { getUserInfo } from '@/services/keycloakService.js'

    import { updateOpgave, deleteOpgave } from '@/services/opgaveService.js'
    import { deleteOpgaveskabelon } from '@/services/opgaveskabelonService.js'
    import { deleteMail, NEW_TASK_ANSVARLIG, NEW_TASK_USER } from '@/services/mailService.js'
    import { downloadRessourceFile } from '@/services/ressourceService.js'

    const router = useRouter()
    const emit = defineEmits(['result-updated'])

    const cardRef = ref(null)
    const isFutureTask = ref(false)
    const userInfo = ref({
        roles: [],
        email: '',
        isAdmin: false,
        isMedarbejder: false,
    })

    const returnDaysFromNow = (date) => {
        const target = new Date(date)
        if (target.toString() === 'Invalid Date') return null

        const now = new Date()
        const toUtcMidnightMs = (d) => Date.UTC(d.getFullYear(), d.getMonth(), d.getDate())
        return Math.round((toUtcMidnightMs(target) - toUtcMidnightMs(now)) / (1000 * 60 * 60 * 24))
    }

    const returnDaysFromNowString = (deadline) => {
        const diffDays = returnDaysFromNow(deadline)
        if (diffDays == null) return ''

        if (diffDays === 1) return 'I morgen'
        else if (diffDays === 0) return 'I dag'
        else if (diffDays === -1) return 'I går'

        const absDays = Math.abs(diffDays)
        const daysText = absDays + ' dag' + (absDays > 1 ? 'e' : '')
        return diffDays < 0 ? `${daysText} siden` : daysText
    }

    const returnFormattedDate = (date) => {
        const d = new Date(date)

        if(d == 'Invalid Date')
            return null

        let formattedDate = d.toLocaleString('da-DK', { month: '2-digit', day: '2-digit' })
        let formattedHourMinute = d.toLocaleString('da-DK', { hour: '2-digit', minute: '2-digit' })

        return formattedDate + ' kl. ' + formattedHourMinute
    }

    const returnFirstAndLastName = (name) => {
        const names = name.split(' ')
        return names.length > 1 ? names[0] + ' ' + names[names.length - 1] : names[0]
    }

    const returnDagOrDage = (days) => {
        return days > 1 ? 'dage' : 'dag'
    }

    const triggerScrollFlash = () => {
        const item = cardRef.value
        if (!item)
            return

        item.classList.remove('scroll-flash')
        void item.offsetWidth
        item.classList.add('scroll-flash')

        setTimeout(() => {
            item.classList.remove('scroll-flash')
        }, 2800)
    }

    function _scrollTo()
    {
        setTimeout(function()
        {
            const item = cardRef.value
            if (!item)
                return

            const rect = item.getBoundingClientRect()
            const topOffset = 45
            const calc = rect.top - topOffset
            window.scrollBy({
                left: 0, top: calc, 
                behavior: "smooth" })

            setTimeout(() => {
                triggerScrollFlash()
            }, 500)
        }, 50) // Wait ms before scrolling
    }

    var props = defineProps({
        id: {
            type: Number,
            required: true
        },
        forloebId: {
            type: Number,
            default: null
        },
        username: {
            type: String
        },
        useremail: {
            type: String
        },
        title: {
            type: String,
            required: true
        },
        header:
        {
            type: String,
            default: ''
        },
        description: {
            type: String,
            default: ''
        },
        note: {
            type: String,
            default: ''
        },
        group: {
            type: Object
        },
        relativeStartdate: {
            type: Number
        },
        relativeEnddate: {
            type: Number
        },
        startdate: {
            type: Date
        },
        deadline: {
            type: Date
        },
        ansvarlig: {
            type: String
        },
        ansvarligEmail: {
            type: String
        },
        booking: {
            type: Date
        },
        result: {
            type: Boolean,
            default: false
        },
        hidden: {
            type: Boolean,
            default: false
        },
        color: {
            type: String,
            default: '000'
        },
        border: {
            type: String,
            default: null
        },
        scrollTo: {
            type: Boolean,
            default: false
        },
        dark: {
            type: Boolean,
            default: false
        },
        templateView: {
            type: Boolean,
            default: false
        },
        isTemplate: {
            type: Boolean,
            default: false
        },
        ressources:
        {
            type: Array,
            default: () => []
        },
        mails: {
            type: Array,
            default: () => []
        },
        sentMails: {
            type: Array,
            default: () => []
        },
        isPreparation:
        {
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

    const dynamicMails = ref(props.mails)
    const dynamicSentMails = ref(props.sentMails)
    const isCollapsed = ref(props.result)

    const resolveMailReceiverLabel = (description) => {
        if (description === NEW_TASK_ANSVARLIG)
            return 'ansvarlig'
        if (description === NEW_TASK_USER)
            return 'ny medarbejder'
        return 'modtager'
    }

    const formatMailSentDate = (sent) => {
        if (!sent)
            return ''

        const parsed = new Date(normalized)
        if (parsed.toString() === 'Invalid Date')
            return ''

        return parsed.toLocaleDateString('da-DK', { year: 'numeric', month: '2-digit', day: '2-digit' })
    }

    /* Task operations */

    const completeTask = (result = true) => {
        updateOpgave(props.id, { result: result }).then(() => {
            emit('result-updated', { id: props.id, result: result })
            if (result)
                isCollapsed.value = true
        }).catch(error => {
            console.error('Error completing task:', error)
        })
    }

    const deleteTask = () => {
        if(!confirm(`Er du sikker på, at du vil slette denne opgave${props.isTemplate ? 'skabelon' : ''}?`))
            return

        if(props.isTemplate)
            deleteOpgaveskabelon(props.id).then(response => {
                const currentPath = { path: router.currentRoute.value.path, query: router.currentRoute.value.query }
                router.replace({ path: '/reload' }).then(() => {
                    router.replace(currentPath)
                })
            }).catch(error => {
                console.error('Error deleting task template:', error)
            })
        else
            deleteOpgave(props.id).then(response => {
                const currentPath = { path: router.currentRoute.value.path, query: router.currentRoute.value.query }
                router.replace({ path: '/reload' }).then(() => {
                    router.replace(currentPath)
                })
            }).catch(error => {
                console.error('Error deleting task:', error)
            })
    }

    const gotoRessource = (id) => {
        const currentQuery = router.currentRoute.value.query
        let updateQuery = { ...currentQuery, item: props.id }
        const ressourcePath = '/forloeb-overview/create-ressource'
        const parentForloebId = props.forloebId ?? currentQuery.id ?? currentQuery.tid
        const isParentTemplateContext = currentQuery.tid != null || (props.templateView && !props.isTemplate)

        let newQuery = {}
        if(props.isTemplate)
            newQuery.tid = id != null ? id : props.id
        else
            newQuery.id = id != null ? id : props.id

        if (props.isTemplate)
            newQuery.template = true

        if (parentForloebId) {
            if (isParentTemplateContext)
                newQuery.forloebTid = parentForloebId
            else
                newQuery.forloebId = parentForloebId
        }

        if(id != null)
            newQuery.edit = true

        router.replace({ query: updateQuery }).then(() => {
            router.push({ path: ressourcePath, query: newQuery })
        })
    }

    const gotoTask = () => {
        const currentQuery = router.currentRoute.value.query
        let updateQuery = { ...currentQuery, item: props.id }
        const taskPath = props.isTemplate ? '/create-opgave' : '/forloeb-overview/create-opgave'
        const parentForloebId = props.forloebId ?? currentQuery.id ?? currentQuery.tid
        const isParentTemplateContext = currentQuery.tid != null || (props.templateView && !props.isTemplate)

        const nextQuery = {
            id: props.id,
            edit: true,
            template: props.isTemplate,
            prep: props.isPreparation,
        }

        if (parentForloebId) {
            if (isParentTemplateContext)
                nextQuery.forloebTid = parentForloebId
            else
                nextQuery.forloebId = parentForloebId
        }

        router.replace({ query: updateQuery }).then(() => {
            router.push({
                path: taskPath,
                query: nextQuery,
            })
        })
    }

    const deletePendingEmail = (id) => {
        if(!confirm('Er du sikker på, at du vil slette denne mail?'))
            return

        deleteMail({ id: id }).then(response => {
            dynamicMails.value = dynamicMails.value.filter(mail => mail.id !== id)
            // const currentPath = { path: router.currentRoute.value.path, query: router.currentRoute.value.query }
            // router.replace({ path: '/reload' }).then(() => {
            //     router.replace(currentPath)
            // })
        }).catch(error => {
            console.error('Error deleting mail:', error)
        })
    }


    const extractFileType = (content_type) => {
        if (!content_type || typeof content_type !== 'string')
            return null

        switch (content_type) {
            case 'application/pdf':
                return 'pdf'
            case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            case 'application/msword':
                return 'word'
            case 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            case 'application/vnd.ms-excel':
                return 'excel'
            case 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
            case 'application/vnd.ms-powerpoint':
                return 'powerpoint'
            default:
                return null
        }
    }


    const extractFilename = (contentDisposition) => {
        if (!contentDisposition || typeof contentDisposition !== 'string')
            return null

        const filenameStar = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i)
        if (filenameStar && filenameStar[1])
        {
            const raw = filenameStar[1].replace(/"/g, '')
            try {
                return decodeURIComponent(raw)
            } catch {
                return raw
            }
        }

        const filename = contentDisposition.match(/filename="?([^";]+)"?/i)
        if (filename && filename[1])
            return filename[1]

        return null
    }

    const downloadRessource = async (ressource) => {
        try {
            const response = await downloadRessourceFile(ressource.RessourceID, {
                external: props.external,
                accessKey: props.accessKey,
            })

            const contentType = response?.headers?.['content-type'] || ressource?.content_type || 'application/octet-stream'
            const blob = new Blob([response.data], { type: contentType })
            const blobUrl = window.URL.createObjectURL(blob)

            const contentDisposition = response?.headers?.['content-disposition']
            const filename = extractFilename(contentDisposition) || ressource?.filename || ressource?.name || 'download'

            const a = document.createElement('a')
            a.href = blobUrl
            a.download = filename
            document.body.appendChild(a)
            a.click()
            a.remove()

            setTimeout(() => window.URL.revokeObjectURL(blobUrl), 1000)
        } catch (error) {
            console.error('Error downloading ressource:', error)
        }
    }

    /* Instantiate */

    onMounted(async () => {
        userInfo.value = await getUserInfo()
        isFutureTask.value = new Date(props.startdate) > new Date()
        if (props.scrollTo) {
            _scrollTo()
        }
    })

    watch(() => props.scrollTo, (scrollTo, previousValue) => {
        if (scrollTo && !previousValue)
            _scrollTo()
    })

    watch(() => props.mails, (mails) => {
        dynamicMails.value = mails || []
    })

    watch(() => props.sentMails, (mails) => {
        dynamicSentMails.value = mails || []
    })
</script>

<template>
    <div :class="['card', 'task', {'dark': dark}, {'collapsed': isCollapsed}, {'hidden-task': hidden}]"
         :style="{ border: border ? `0.1rem dashed #${border}` : 'none' }"
         ref="cardRef"
         @click="isCollapsed ? isCollapsed = false : null">

        <div class="card-group no-select" @click.stop="isCollapsed = !isCollapsed">
            {{ group?.name }}

            <span :class="['group-status', 'complete']" v-if="result">
                <i class="fa-solid fa-circle-check"></i>
            </span>
            <span :class="['group-status', 'overdue']" v-if="!result && !templateView && !isPreparation && new Date(deadline) < new Date()">
                Deadline overskredet <i class="fa-solid fa-triangle-exclamation"></i>
            </span>
            <span :class="['group-status', 'upcoming']" v-if="!result && !templateView && !isPreparation && new Date(startdate) > new Date()">
                <i class="fa-solid fa-clock"></i>
            </span>
            <span :class="['group-status', 'ongoing']" v-if="startdate && !isFutureTask && !isPreparation && !templateView && !result && new Date(deadline) >= new Date()">
                <i class="fa-solid fa-circle"></i>
            </span>
            <span class="group-note" v-if="hidden">
                Skjult for medarbejder <i class="fa-solid fa-eye-slash"></i>
            </span>

        </div>

        <div class="card-color-seperator" :style="`background-color: #`+ color +`;`"></div>

        <div class="card-header">
            <div style="width:100%">
                <span class="card-inline-title" v-if="title != null && title != ''">
                    {{ title }}
                </span>
                <span class="card-description">{{ description }}</span>
            </div>
        </div>

        <div class="ressources" v-if="props.ressources.length > 0">
            <template v-if="!userInfo?.isAdmin && userInfo?.email != ansvarligEmail">
                <div v-for="ressource in ressources" :key="ressource.RessourceID">
                    <a v-if="!ressource.isFile"
                        :href="ressource.url"
                        target="_blank"
                        class="ressource">
                        <i class="fa-solid fa-up-right-from-square"></i>
                        {{ ressource.name }}
                        <div class="file-name">{{ ressource.url }}</div>
                    </a>
                    <div v-else
                        @click="downloadRessource(ressource)"
                        class="ressource">
                        <i :class="'fa-regular fa-file' + (extractFileType(ressource.content_type) ? '-' + extractFileType(ressource.content_type) : '')"></i>
                        {{ ressource.name }}
                        <div class="file-name">{{ ressource.filename || ressource.url }}</div>
                    </div>
                </div>
            </template>
            <template v-else>
                <div v-for="ressource in ressources"
                    :key="ressource.RessourceID"
                    @click="gotoRessource(ressource.RessourceID)"
                    class="ressource">
                    <i class="fa-solid fa-pen-to-square"></i>
                    {{ ressource.name }}
                    <div class="file-name">{{ ressource.filename || ressource.url }}</div>
                </div>
            </template>
        </div>

        <div class="card-details">

            <div v-if="(templateView && !isTemplate) || isPreparation">
                <div class="icon"><i class="fa-regular fa-clock"></i></div>
                <div class="text">
                    <div class="small faded">Startdag</div>
                    <div>{{ relativeStartdate == 0 ? 'Ved forløbets start' : Math.abs(relativeStartdate) + ' ' + returnDagOrDage(Math.abs(relativeStartdate)) + (relativeStartdate > 0 ? ' efter opstart' : ' før opstart') }}</div>
                </div>
            </div>

            <div v-if="isFutureTask">
                <div class="icon"><i class="fa-solid fa-calendar"></i></div>
                <div class="text">
                    <div class="small faded">Starter {{ (returnDaysFromNow(startdate) > 1 ? ' om ' : '') }}</div>
                    <div>{{ returnDaysFromNowString(startdate) }}</div>
                </div>
            </div>

            <div v-if="isTemplate || templateView || isPreparation">
                <div class="icon"><i class="fa-solid fa-clock"></i></div>
                <div class="text">
                    <div class="small faded">Varighed</div>
                    <div>{{ relativeEnddate + ' ' + returnDagOrDage(relativeEnddate)}}</div>
                </div>
            </div>

            <div v-if="!isTemplate && !templateView && !isPreparation"
                :class="!result && !templateView && !isPreparation && new Date(deadline) < new Date() ? 'overdue' : ''">
                <div class="icon"><i class="fa-solid fa-clock"></i></div>
                <div class="text">
                    <div class="small faded">Deadline</div>
                    <div>{{ returnDaysFromNowString(deadline) }}</div>
                </div>
            </div>

            <div v-if="!templateView && ansvarlig">
                <div class="icon"><i class="fa-solid fa-user"></i></div>
                
                <div class="text" v-if="forloebId != null && userInfo.email.toLowerCase() == ansvarligEmail?.toLowerCase()">
                    <div class="small faded">Medarbejder</div>
                    <div>{{ username ?? 'Ukendt medarbejder' }}</div>
                </div>
                <div class="text" v-else>
                    <div class="small faded">Ansvarlig</div>
                    <div>{{ ansvarlig ? returnFirstAndLastName(ansvarlig) : 'Ingen' }}</div>
                </div>
            </div>

            <div v-if="!templateView && !isPreparation && booking">
                <div class="icon"><i class="fa-solid fa-calendar"></i></div>
                <div class="text">
                    <div class="small faded">Booking</div>
                    <div>{{booking && returnFormattedDate(booking) != null ? returnFormattedDate(booking) : 'Ingen'}}</div>
                </div>
            </div>

        </div><!-- /card-details -->

        <div v-if="note != null && note != ''" class="notes">
            <div style='font-size: 0.8em; color: var(--color-card-text);letter-spacing: 0.025rem;padding-bottom: 0.5rem'>
                <i class='fa-solid fa-note-sticky' style='padding-right: 0.5rem'></i>
                Note til ansvarlig:
            </div>
            
            {{ note }}
        </div>

        <div class="buttons" v-if="isTemplate || userInfo?.isAdmin || (userInfo?.email != null && userInfo?.email != '' && (userInfo?.email?.toLowerCase() == ansvarligEmail?.toLowerCase() || (userInfo?.email?.toLowerCase() == useremail?.toLowerCase() && (ansvarligEmail == '' || ansvarligEmail == null))))">
            <div class="button"
                    v-if="isTemplate || userInfo?.isAdmin || (userInfo?.email != null && userInfo?.email != '' && userInfo?.email?.toLowerCase() == ansvarligEmail?.toLowerCase())"
                    @click="gotoRessource()">
                    + Tilføj ressource
            </div>

            <div class="button hollow"
                    v-if="isTemplate || userInfo?.isAdmin"
                    @click="gotoTask()">
                    Redigér
            </div>

            <div :class="['button', 'hollow', {'yellow': result}]"
                    v-if="!templateView && !isPreparation && 
                        (userInfo?.isAdmin ||
                            (userInfo?.email != null && userInfo?.email != '') &&
                            (
                                (userInfo.email.toLowerCase() == ansvarligEmail?.toLowerCase()) ||
                                (userInfo?.email?.toLowerCase() == useremail?.toLowerCase() && (ansvarligEmail == '' || ansvarligEmail == null))
                            )
                        )"
                    @click="completeTask(!result)">
                    Markér {{ result ? 'ej ' :'' }} gennemført
            </div>

            <div class="button hollow red"
                    v-if="isTemplate || userInfo?.isAdmin"
                    @click="deleteTask()">
                    Slet
            </div>

            <router-link class="button hollow"
                            v-if="(userInfo?.isAdmin && forloebId != null) || (userInfo?.email != null && userInfo?.email != '' && userInfo?.email?.toLowerCase() == ansvarligEmail?.toLowerCase() && forloebId != null)"
                            :to="`/forloeb-overview?id=${forloebId}`">
                            Gå til forløb
            </router-link>
        </div><!-- /buttons -->

        <div class="mails" v-if="dynamicMails.length > 0 || dynamicSentMails.length > 0">
            <div class="mail sent" v-for="mail in dynamicSentMails" :key="`sent-${mail.id}`">
                <div>
                    <div class="nowrap">Notifikation sendt til {{ resolveMailReceiverLabel(mail.description) }}</div>
                    <div class="mail-recipient"><i class="fa-solid fa-envelope"></i> {{ mail.recipient }} <i class="fa-solid fa-clock"></i> {{ returnFormattedDate(mail.sent) }}</div>
                </div>
                <i class="fa-solid fa-circle-check"></i>
            </div>

            <div class="mail" v-for="mail in dynamicMails" :key="mail.id">
                <div>
                    <div class="nowrap">Notifikation planlagt til {{ resolveMailReceiverLabel(mail.description) }}</div>
                    <div class="mail-recipient nowrap"><i class="fa-solid fa-envelope"></i> {{ mail.recipient }}</div>
                </div>
                <i @click="deletePendingEmail(mail.id)" class="fa-solid fa-circle-xmark"></i>
            </div>
        </div><!-- /mails -->

    </div><!-- /card -->

</template>

<style scoped>
    @keyframes subtle-outline-blink {
        0%, 100% {
            outline-color: rgba(108, 126, 138, 0);
        }
        20%, 55%, 85% {
            outline-color: rgba(108, 126, 138, 0.55);
        }
        35%, 70%, 95% {
            outline-color: rgba(108, 126, 138, 0);
        }
    }

    .task.scroll-flash {
        outline: 0.2rem solid rgba(143, 143, 162, 0);
        outline-offset: 0.05rem;
        animation: subtle-outline-blink 2.5s ease-in-out;
    }

    .notes {
        background-color: rgb(247, 248, 210);
        padding: 0.5rem 0.8rem;
        border-radius: 0.4rem;
        white-space: pre-line;
    }
    .card-group {
        width: 100%;
        font-size: 0.8em;
        border-top-left-radius: 0.35rem;
        border-top-right-radius: 0.35rem;
        background-color: rgba(145, 135, 130, 0.16);
        padding: 0.5rem 0.6rem;
        cursor: pointer;
    }
    .card-group:has(.group-status.complete) {
        background-color: rgba(34, 152, 16, 0.05);
    }
    .card-group:has(.group-status.overdue) {
        background-color: rgba(177, 21, 21, 0.05);
    }
    .card-group:has(.group-status.ongoing) {
        background-color: rgba(24, 17, 171, 0.05);
    }

    .task {
        position: relative;
        overflow: hidden;
        max-height: 80rem;
        transition: max-height 300ms ease;
    }

    .task.hidden-task {
        background-color: var(--color-card-yellow);
    }

    .task::after {
        content: '';
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        height: 2.8rem;
        opacity: 0;
        pointer-events: none;
        transition: opacity 220ms ease;
    }

    .collapsed {
        max-height: 6rem;
        cursor: pointer;
        mask-image: linear-gradient(to bottom, black 55%, transparent 85%);
        margin-bottom: 1rem;
        clip-path: inset(0 0 1rem 0);
        transition: max-height 300ms ease, clip-path 220ms ease;
    }

    .collapsed::after {
        opacity: 1;
    }

    .collapsed:hover {
        clip-path: inset(0 0 0 0);
        mask-image: linear-gradient(to bottom, black 70%, transparent 100%);
    }

    .group-note {
        float: right;
        font-style: italic;
        opacity: 0.6;
        margin-left: 0.2rem;
    }
    .group-note i, .group-status i {
        margin-left: 0.3rem;
        font-size: 0.9em;
    }
    .group-status {
        float: right;
        margin-left: 0.4rem;
    }
    .group-status.complete {
        color: #2e7b22;
        opacity: 0.6;
        font-style: italic;
        opacity: 0.6;
    }
    .group-status.overdue {
        color: #b11515;
    }
    .group-status.ongoing {
        color: #211a84; 
        opacity: 0.6;
    }
    .group-status.upcoming {
        color: #777371;
        font-style: italic;
        opacity: 0.6;
    }

    .mails {
        border-top: 0.1rem solid var(--color-background);
        background-color: rgba(145, 135, 130, 0.16);
        display: flex;
        flex-direction: column;
    }
    .mail {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.4rem 0.6rem;
        transition: background-color 200ms ease;
    }
    .mail.sent {
        background-color: rgba(29, 99, 24, 0.1);
    }
    .mail:not(.sent):has(i:hover) {
        background-color: rgba(145, 135, 130, 0.15);
    }
    .mail i {
        cursor: pointer;
        color: var(--color-card-text);
    }
    .mail.sent i {
        color: #617a5d;
        cursor: default;
    }
    .mail > div:first-child {
        display: flex;
        flex-direction: column;
        font-size: 0.8em;
    }
    .mail .mail-recipient {
        opacity: 0.7;
        font-size: 0.9em;
    }
    .mail-recipient i {
        margin-right: 0.1rem;
        font-size: 0.85em;
        color: var(--color-card-text)!important;
    }
    .mail-recipient i:not(:first-of-type) {
        margin-left: 0.5rem;
    }


</style>