<script setup>
    import { ref, onMounted } from 'vue'
    import { useRouter } from 'vue-router'

    import { updateOpgave, deleteOpgave } from '@/services/opgaveService.js'
    import { deleteOpgaveskabelon } from '@/services/opgaveskabelonService.js'
    import { deleteMail } from '@/services/mailService.js'

    const router = useRouter()

    const cardRef = ref(null)
    const isFutureTask = ref(false)

    const expandCard = () => {
        cardRef.value.classList.toggle('expand-content')
    }

    const returnDaysFromNow = (date) => {
        const target = new Date(date)
        const now = new Date()
        const toUtcMidnightMs = (d) => Date.UTC(d.getFullYear(), d.getMonth(), d.getDate())
        return Math.round((toUtcMidnightMs(target) - toUtcMidnightMs(now)) / (1000 * 60 * 60 * 24))
    }

    const returnTimeLeft = (deadline) => {
        const target = new Date(deadline)
        if (target.toString() === 'Invalid Date') return ''

        const now = new Date()
        const toUtcMidnightMs = (d) => Date.UTC(d.getFullYear(), d.getMonth(), d.getDate())
        const diffDays = Math.round((toUtcMidnightMs(target) - toUtcMidnightMs(now)) / (1000 * 60 * 60 * 24))

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

    function scrollTo()
    {
        setTimeout(function()
        {
            const item = cardRef.value
            let rect = item.getBoundingClientRect()
            let calc = rect.top - (window.innerHeight / 2) + (item.offsetHeight / 2)
            window.scrollBy({
                left: 0, top: calc, 
                behavior: "smooth" })
        }, 50) // Wait ms before scrolling
    }

    var props = defineProps({
        id: {
            type: Number,
            required: true
        },
        userInfo: {
            type: Object,
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
        expandByDefault: {
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
        }
    })

    const dynamicMails = ref(props.mails)

    const renderNoteHTML = (note) => {
        const header = "<div style='font-size: 0.8em; color: var(--color-card-text);letter-spacing: 0.025rem;padding-bottom: 0.5rem'>"
                     + "<i class='fa-solid fa-note-sticky' style='padding-right: 0.5rem'></i>Note til ansvarlig:</div>"
        return header + note.replace(/\n/g, '<br />')
    }

    /* Task operations */

    const completeTask = (result = true) => {
        updateOpgave(props.id, { result: result }).then(response => {
            const currentPath = { path: router.currentRoute.value.path, query: router.currentRoute.value.query }
            router.replace({ path: '/reload' }).then(() => {
                router.replace(currentPath)
            })
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

        let newQuery = {}
        if(props.isTemplate)
            newQuery.tid = id != null ? id : props.id
        else
            newQuery.id = id != null ? id : props.id
        if(id != null)
            newQuery.edit = true

        router.replace({ query: updateQuery }).then(() => {
            router.push({ path: '/create-ressource', query: newQuery })
        })
    }

    const gotoTask = () => {
        const currentQuery = router.currentRoute.value.query
        let updateQuery = { ...currentQuery, item: props.id }

        router.replace({ query: updateQuery }).then(() => {
            router.push({ path: '/create-opgave', query: { id: props.id, edit: true, template: props.isTemplate, prep: props.isPreparation } })
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

    /* Instantiate */

    onMounted(() => {
        isFutureTask.value = new Date(props.startdate) > new Date()
        if (props.expandByDefault) {
            scrollTo()
        }
    })
</script>

<template>
    <div :class="['card', { 'expand-content': expandByDefault }, {'dark': dark}]" :style="{ border: border ? `0.1rem dashed #${border}` : 'none' }" ref="cardRef">
        <div class="card-header pointer no-select" @click="e => { if (!e.target.closest('.tooltip')) expandCard() }">
            <div class="card-icon">
                <div :style="`background-color: #`+ color +`;`" class="tooltip-hover">
                    <div>{{ group?.letter }}</div>
                    <span v-if="group != null" class="tooltip-display">{{ group?.name }}</span>
                </div>
            </div>

            <div class="no-overflow">
                <p class="card-title">
                    {{ title }}
                </p>
                <p class="card-subtitle">
                    {{ header }}
                </p>
            </div>

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
                                <div class="nowrap">Notifikation</div>
                                <div class="mail-recipient nowrap">{{ mail.recipient }}</div>
                            </div>
                            <i @click="deletePendingEmail(mail.id)" class="fa-solid fa-circle-xmark"></i>
                        </div>
                    </div>
                </div>
            </div>

            <!-- <div class="card-image" :style="`background-image: url('`+ image +`');`">
                &nbsp;
            </div> -->
        </div>

        <!-- <div class="card-large-image" :style="`background-image: url('`+ image +`');`">
            &nbsp;
        </div> -->
        <div class="card-color-seperator" :style="`background-color: #`+ color +`;`">
        </div>

        <div class="card-content">
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
                        <div>{{ templateView || isPreparation ? relativeEnddate + ' ' + returnDagOrDage(relativeEnddate) : returnTimeLeft(isFutureTask ? startdate : deadline) }}</div>
                    </div>
                </div>

                <div v-if="!templateView">
                    <div class="icon"><i class="fa-solid fa-user"></i></div>
                    
                    <div class="text" v-if="forloebId != null && (userInfo.isAnsvarlig && userInfo.email == ansvarligEmail)">
                        <div class="small faded">Medarbejder</div>
                        <div>{{ username ?? 'Ukendt medarbejder' }}</div>
                    </div>
                    <div class="text" v-else>
                        <div class="small faded">Ansvarlig</div>
                        <div>{{ ansvarlig ? returnFirstAndLastName(ansvarlig) : 'Ingen ansvarlig' }}</div>
                    </div>
                </div>

                <div v-if="!templateView && !isPreparation">
                    <div class="icon"><i class="fa-solid fa-calendar"></i></div>
                    <div class="text">
                        <div class="small faded">Booking</div>
                        <div>{{booking && returnFormattedDate(booking) != null ? returnFormattedDate(booking) : 'Ingen kalenderbooking'}}</div>
                    </div>
                </div>

            </div>

            <p v-html="description.replace(/\n/g, '<br>')"></p>

            <div class="ressources" v-if="props.ressources.length > 0">
                <span class="faded uppercase">Ressourcer</span>

                <a v-if="!userInfo?.isAdmin && userInfo?.email != ansvarligEmail"
                   v-for="ressource in ressources"
                   :href="ressource.url"
                   target="_blank"
                   class="link tooltip-hover">
                        <i class="fa-solid fa-up-right-from-square"></i>
                        {{ ressource.name }}
                        <span v-if="ressource != null" class="tooltip-display">{{ ressource.url }}</span>
                </a>
                <span v-else v-for="ressource in ressources"
                      @click="gotoRessource(ressource.RessourceID)"
                      class="link tooltip-hover">
                        <i class="fa-solid fa-pen-to-square"></i>
                        {{ ressource.name }}
                        <span v-if="ressource != null" class="tooltip-display">{{ ressource.url }}</span>
                </span>
            </div>

            <p v-if="note != null && note != ''" class="notes" v-html="renderNoteHTML(note)"></p>

            <div class="buttons">
                <div class="button"
                     v-if="isTemplate || userInfo?.isAdmin || (userInfo?.isAnsvarlig && userInfo?.email == ansvarligEmail)"
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
                                (userInfo?.isAnsvarlig && userInfo?.email == ansvarligEmail) ||
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
                             v-if="userInfo?.email == ansvarligEmail && forloebId != null"
                             :to="`/forloeb-overview?id=${forloebId}`">
                                Gå til forløb
                </router-link>
            </div><!-- /buttons -->

        </div><!-- /card-content -->
    </div><!-- /card -->

</template>

<style scoped>
    .notes {
        background-color: rgb(247, 248, 210);
        padding: 0.5rem 0.8rem;
        border-radius: 0.4rem;
        margin-top: 1rem;
        transform: translateY(0.5rem);
    }
    .tooltipContainer {
        position: relative;
    }
    .tooltip {
        background-color: var(--color-card-dark);
        padding: 0.5rem 0.8rem;
        border-radius: 0.4rem;

        visibility: hidden;
        opacity: 0;
        position: absolute;
        right: -0.75rem;

        font-size: 0.75rem;
        cursor: default;
        text-align: right;

        max-height: 4rem;
        overflow-y: auto;
        user-select: text;

        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 0.4rem;
    }
    .tooltip > .mail {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    .mail-recipient {
        max-width: 15rem;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 0.9em;
        font-weight: 400;
    }
    .tooltip i {
        margin-left: 0.5rem;
        font-size: 1rem;
    }
    .tooltip i:hover {
        color: var(--color-button-red);
        cursor: pointer;
    }
    .tooltipContainer:hover > .tooltip {
        visibility: visible;
        opacity: 1;
    }
</style>