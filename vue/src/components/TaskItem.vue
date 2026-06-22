<script setup>
    import { ref, onMounted, watch } from 'vue'
    import { useRouter } from 'vue-router'

    import { getUserInfo } from '@/services/keycloakService.js'

    import { updateOpgave, deleteOpgave } from '@/services/opgaveService.js'
    import { deleteOpgaveskabelon } from '@/services/opgaveskabelonService.js'
    import { deleteMail, NEW_TASK_ANSVARLIG } from '@/services/mailService.js'
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

        if (diffDays === 0) return 'I dag'
        if (diffDays === 1) return 'I morgen'
        if (diffDays === -1) return 'I går'

        const absDays = Math.abs(diffDays)
        const daysText = absDays + ' dag' + (absDays > 1 ? 'e' : '')
        return diffDays < 0 ? `${daysText} siden` : daysText
    }

    const returnFormattedDate = (date) => {
        const d = new Date(date)

        if(d == 'Invalid Date')
            return null

        return d.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit' }) + ' ' + d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
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

    /* Task operations */

    const completeTask = (result = true) => {
        updateOpgave(props.id, { result: result }).then(() => {
            emit('result-updated', { id: props.id, result: result })
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
</script>

<template>
    <div :class="['card', 'task', {'dark': dark}]" :style="{ border: border ? `0.1rem dashed #${border}` : 'none' }" ref="cardRef">

        <div class="card-group">{{ group?.name }}</div>

        <div class="card-color-seperator" :style="`background-color: #`+ color +`;`"></div>

        <div class="card-header">

            <div style="width:100%">


                <!-- <div class="card-icon no-select">
                    <div :style="`position:relative;background-color: #`+ color +`;`" class="tooltip-hover">
                        <div>{{ group?.letter }}</div>
                        <span v-if="group != null" class="tooltip-display">{{ group?.name }}</span>
                    </div>
                </div> -->

                <span class="card-inline-title">
                    {{ title }}
                </span>
                <span class="card-description">{{ description }}</span>

            </div>

            <!-- 
            <div class="card-separator"></div>
            
            <div class="card-details" v-if="props.duration == null && dynamicMails.length > 0">
                <div class="tooltipContainer">
                    <div class="icon"><i class="fa-solid fa-envelope"></i></div>
                    <div class="text">
                        <div class="small faded">Mails</div>
                        <div>{{ dynamicMails.length > 0 ? (dynamicMails.length + ' planlagt') : 'Ingen mails' }}</div>
                    </div>
                    
                    <div class="tooltip">
                        <div class="mail" v-for="mail in dynamicMails" :key="mail.id">
                            <div>
                                <div class="nowrap">Notifikation til {{ mail.description == NEW_TASK_ANSVARLIG ? 'ansvarlig' : 'ny medarbejder' }}</div>
                                <div class="mail-recipient nowrap">{{ mail.recipient }}</div>
                            </div>
                            <i @click="deletePendingEmail(mail.id)" class="fa-solid fa-circle-xmark"></i>
                        </div>
                    </div>
                </div>
            </div> -->
        </div>

        <div class="ressources" v-if="props.ressources.length > 0">
            <template v-if="!userInfo?.isAdmin && userInfo?.email != ansvarligEmail">
                <div v-for="ressource in ressources" :key="ressource.RessourceID">
                    <a v-if="!ressource.isFile"
                        :href="ressource.url"
                        target="_blank"
                        class="ressource tooltip-hover">
                        <i class="fa-solid fa-up-right-from-square"></i>
                        {{ ressource.name }}
                        <span v-if="ressource != null" class="tooltip-display">{{ ressource.url }}</span>
                    </a>
                    <span v-else
                        @click="downloadRessource(ressource)"
                        class="ressource tooltip-hover">
                        <i :class="'fa-regular fa-file' + (extractFileType(ressource.content_type) ? '-' + extractFileType(ressource.content_type) : '')"></i>
                        {{ ressource.name }}
                        <span v-if="ressource != null" class="tooltip-display">{{ ressource.filename || ressource.url }}</span>
                    </span>
                </div>
            </template>
            <template v-else>
                <div v-for="ressource in ressources"
                    :key="ressource.RessourceID"
                    @click="gotoRessource(ressource.RessourceID)"
                    class="ressource tooltip-hover">
                    <i class="fa-solid fa-pen-to-square"></i>
                    {{ ressource.name }}
                    <div class="file-name">{{ ressource.filename || ressource.url }}</div>

                    <!-- <span v-if="ressource != null" class="tooltip-display">{{ ressource.isFile ? (ressource.filename || ressource.url) : ressource.url }}</span> -->
                </div>
            </template>
        </div>

        <div class="card-details">

            <div v-if="(templateView && !isTemplate) || isPreparation">
                <div class="icon"><i class="fa-solid fa-clock"></i></div>
                <div class="text">
                    <div class="small faded">Startdag</div>
                    <div>{{ relativeStartdate == 0 ? 'Ved forløbets start' : Math.abs(relativeStartdate) + ' ' + returnDagOrDage(Math.abs(relativeStartdate)) + (relativeStartdate > 0 ? ' efter opstart' : ' før opstart') }}</div>
                </div>
            </div>

            <div>
                <div class="icon"><i class="fa-solid fa-clock"></i></div>
                <div class="text">
                    <div class="small faded">{{ templateView || isPreparation ? 'Varighed' : isFutureTask ? ('Starter' + (returnDaysFromNow(startdate) > 1 ? ' om ' : '')) : 'Deadline' }}</div>
                    <div>{{ templateView || isPreparation ? relativeEnddate + ' ' + returnDagOrDage(relativeEnddate) : returnDaysFromNowString(isFutureTask ? startdate : deadline) }}</div>
                </div>
            </div>

            <div v-if="!templateView">
                <div class="icon"><i class="fa-solid fa-user"></i></div>
                
                <div class="text" v-if="forloebId != null && userInfo.email == ansvarligEmail">
                    <div class="small faded">Medarbejder</div>
                    <div>{{ username ?? 'Ukendt medarbejder' }}</div>
                </div>
                <div class="text" v-else>
                    <div class="small faded">Ansvarlig</div>
                    <div>{{ ansvarlig ? returnFirstAndLastName(ansvarlig) : 'Ingen' }}</div>
                </div>
            </div>

            <div v-if="!templateView && !isPreparation">
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

        <div class="buttons">
            <div class="button"
                    v-if="isTemplate || userInfo?.isAdmin || (userInfo?.email != null && userInfo?.email != '' && userInfo?.email == ansvarligEmail)"
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
                            (userInfo?.email != null && userInfo?.email != '' && userInfo?.email == ansvarligEmail) ||
                            (userInfo?.isMedarbejder && ansvarligEmail == '')
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
                            v-if="(userInfo?.isAdmin && forloebId != null) || (userInfo?.email != null && userInfo?.email != '' && userInfo?.email == ansvarligEmail && forloebId != null)"
                            :to="`/forloeb-overview?id=${forloebId}`">
                            Gå til forløb
            </router-link>
        </div><!-- /buttons -->

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
        padding: 0.5rem 1rem;
    }
</style>