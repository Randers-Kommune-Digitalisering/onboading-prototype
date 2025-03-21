<script setup>
    import { ref, onMounted } from 'vue'
    import { useRouter } from 'vue-router'

    import { getRessourcesByOpgaveID, getRessourcesByOpgaveskabelonID  } from '@/services/ressourceService'
    import { updateOpgave, deleteOpgave } from '@/services/opgaveService'
    import { deleteOpgaveskabelon } from '@/services/opgaveskabelonService'

    const router = useRouter()

    const cardRef = ref(null)
    const ressourceList = ref([])
    const isFutureTask = ref(false)

    const expandCard = () => {
        cardRef.value.classList.toggle('expand-content')
    }

    const returnTimeLeft = (deadline) => {
        const now = new Date()
        const diff = deadline - now
        const absDiff = Math.abs(diff)
        const days = Math.floor(absDiff / (1000 * 60 * 60 * 24))
        const hours = Math.floor((absDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
        const minutes = Math.floor((absDiff % (1000 * 60 * 60)) / (1000 * 60))
        const daysText = days > 0 ? days + ' dag' + (days > 1 ? 'e' : '') : ''
        const hoursText = hours > 0 ? hours + ' time' + (hours > 1 ? 'r' : '') : ''
        const minutesText = minutes > 0 ? minutes + ' minut' + (minutes > 1 ? 'ter' : '') : ''
        const timeLeft = `${days > 0 ? daysText : ''} ${hours > 0 ? hoursText : ''} ${minutes > 0 && hours === 0 ? (minutesText) : ''}`
        return diff < 0 ? `${timeLeft} siden` : timeLeft
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

    var props = defineProps({
        id: {
            type: Number,
            required: true
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
        responsible: {
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
        adminView: {
            type: Boolean,
            default: false
        },
        expandByDefault: {
            type: Boolean,
            default: false
        },
        dark: {
            type: Boolean,
            required: false,
            default: false
        },
        templateView: {
            type: Boolean,
            default: false
        },
        isTemplate: {
            type: Boolean,
            default: false
        }
    })

    /* Complete task */
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

    /* Instantiate */

    onMounted(() => {
        if(props.isTemplate)
            getRessourcesByOpgaveskabelonID(props.id).then(response => {
                ressourceList.value = response.data
            }).catch(error => {
                console.error('Error fetching ressources:', error)
            })
        else
            getRessourcesByOpgaveID(props.id).then(response => {
                ressourceList.value = response.data
            }).catch(error => {
                console.error('Error fetching ressources:', error)
            })

        isFutureTask.value = new Date(props.startdate) > new Date()
    })
</script>

<template>
    <div :class="['card', { 'expand-content': expandByDefault }, {'dark': dark}]" ref="cardRef">
        <div class="card-header pointer no-select" @click="expandCard">
            <div class="card-icon">
                <div :style="`background-color: #`+ color +`;`">
                    <div>{{ title.slice(0,1).toLocaleLowerCase() }}</div>
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
                <div v-if="templateView && !isTemplate">
                    <div class="icon"><i class="fa-solid fa-clock"></i></div>
                    <div class="text">
                        <div class="small faded">Startdag</div>
                        <div>{{ relativeStartdate == 0 ? 'Ved forløbets start' : relativeStartdate + ' ' + returnDagOrDage(relativeStartdate) + ' efter opstart' }}</div>
                    </div>
                </div>

                <div>
                    <div class="icon"><i class="fa-solid fa-clock"></i></div>
                    <div class="text">
                        <div class="small faded">{{ templateView ? 'Varighed' : isFutureTask ? 'Starter om' : 'Deadline' }}</div>
                        <div>{{ templateView ? relativeEnddate + ' ' + returnDagOrDage(relativeEnddate) : returnTimeLeft(isFutureTask ? startdate : deadline) }}</div>
                    </div>
                </div>

                <div v-if="!templateView">
                    <div class="icon"><i class="fa-solid fa-user"></i></div>
                    <div class="text">
                        <div class="small faded">Ansvarlig</div>
                        <div>{{ responsible ? returnFirstAndLastName(responsible) : 'Ingen ansvarlig' }}</div>
                    </div>
                </div>

                <div v-if="!templateView">
                    <div class="icon"><i class="fa-solid fa-calendar"></i></div>
                    <div class="text">
                        <div class="small faded">Booking</div>
                        <div>{{booking && returnFormattedDate(booking) != null ? returnFormattedDate(booking) : 'Ingen kalenderbooking'}}</div>
                    </div>
                </div>

            </div>

            <p v-html="description.replace(/\n/g, '<br>')"></p>

            <div class="ressources" v-if="ressourceList.length > 0">
                <span class="faded uppercase">Ressourcer</span>
                <a v-if="!props.adminView" v-for="ressource in ressourceList" :href="ressource.url" target="_blank" class="link">
                    <i class="fa-solid fa-up-right-from-square"></i>
                    {{ ressource.name }}
                </a>
                <router-link v-else v-for="ressource in ressourceList" :to="`/create-ressource?id=${ressource.RessourceID}&edit=true`" class="link">
                    <i class="fa-solid fa-up-right-from-square"></i>
                    {{ ressource.name }}
                </router-link>
            </div>

            <div class="buttons">
                <router-link class="button" v-if="adminView" :to="`/create-ressource?${templateView ? 't' : ''}id=${id}`">+ Tilføj ressource</router-link>
                <router-link class="button hollow" v-if="adminView" :to="`/create-opgave?edit=true&id=${id}${isTemplate ? '&template=true' : ''}`">Redigér</router-link>
                <div :class="['button', 'hollow', {'red': props.result}]" v-if="!templateView && ((!props.adminView && props.responsible == '') || props.adminView)" @click="completeTask(!props.result)">Markér {{ props.result ? 'ej ' :'' }} gennemført</div>
                <div class="button hollow red" v-if="adminView" @click="deleteTask()">Slet</div>
            </div>
        </div>
    </div>

</template>