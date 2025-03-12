<script setup>
    import { ref, onMounted } from 'vue'

    import { getRessourcesByOpgaveID  } from '@/services/ressourceService'

    const cardRef = ref(null)
    const ressourceList = ref([])

    const expandCard = () => {
        cardRef.value.classList.toggle('expand-content')
    }

    const returnTimeLeft = (deadline) => {
        const now = new Date()
        const diff = deadline - now
        const days = Math.floor(diff / (1000 * 60 * 60 * 24))
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
        const daysText = days > 0 ? days + ' dag' + (days > 1 ? 'e' : '') : ''
        const hoursText = hours > 0 ? hours + ' time' + (hours > 1 ? 'r' : '') : ''
        const minutesText = minutes > 0 ? minutes + ' minut' + (minutes > 1 ? 'ter' : '') : ''
        return `${days > 0 ? daysText : ''} ${hours > 0 ? hoursText : ''} ${minutes > 0 && hours === 0 ? (minutesText) : ''}`
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
        deadline: {
            type: Date
        },
        responsible: {
            type: String
        },
        booking: {
            type: Date
        },
        image: {
            type: String,
            default: ''
        },
        color: {
            type: String,
            default: '000'
        },
        link: {
            type: String
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
        }
    })

    /* Instantiate */

    onMounted(() => {
        getRessourcesByOpgaveID(props.id).then(response => {
            ressourceList.value = response.data
        }).catch(error => {
            console.error('Error fetching ressources:', error)
        })
    })
</script>

<template>

    <div :class="['card', { 'expand-content': expandByDefault }, {'dark': dark}]" ref="cardRef">
        <div class="card-header pointer no-select" @click="expandCard">
            <div class="card-icon">
                <div :style="`background-color: #`+ color +`;`">
                    <div>i</div>
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
                <div>
                    <div class="icon"><i class="fa-solid fa-clock"></i></div>
                    <div class="text">
                        <div class="small faded">Deadline</div>
                        <div>{{ deadline ? returnTimeLeft(deadline) : 'Ingen deadline' }}</div>
                    </div>
                </div>

                <div>
                    <div class="icon"><i class="fa-solid fa-user"></i></div>
                    <div class="text">
                        <div class="small faded">Ansvarlig</div>
                        <div>{{ responsible ? returnFirstAndLastName(responsible) : 'Ingen ansvarlig' }}</div>
                    </div>
                </div>

                <div>
                    <div class="icon"><i class="fa-solid fa-calendar"></i></div>
                    <div class="text">
                        <div class="small faded">Booking</div>
                        <div>{{booking && returnFormattedDate(booking) != null ? returnFormattedDate(booking) : 'Ingen kalenderbooking'}}</div>
                    </div>
                </div>
            </div>

            <p>{{ description }}</p>

            <div class="ressources" v-if="ressourceList.length > 0">
                <span class="faded uppercase">Ressourcer</span>
                <a v-for="ressource in ressourceList" :href="ressource.url" target="_blank" class="link">
                    <i class="fa-solid fa-up-right-from-square"></i>{{ ressource.name }}</a>
            </div>

            <div class="buttons">
                
                <router-link v-if="adminView" :to="`/create-ressource?id=${id}`" class="button">+ Tilføj ressource</router-link>
                <div class="button disabled" v-if="adminView">Redigér</div>
                <!--div class="button" v-if="link">Gå til kursus</div-->
                <div class="button disabled">Markér gennemført</div>
            </div>
        </div>
    </div>

</template>