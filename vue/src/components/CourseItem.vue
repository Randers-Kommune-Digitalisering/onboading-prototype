<script setup>
    import { ref } from 'vue'
    import ProgressBar from './ProgressBar.vue'
    var cardRef = ref(null)

    const returnFormattedDate = (date) => {
        const d = new Date(date)
        return d.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit' }) // + ' ' + d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
    }

    const props = defineProps({
        id: {
            type: Number,
            required: true
        },
        title: {
            type: String,
            required: true
        },
        name:
        {
            type: String
        },
        startDate : {
            type: Date
        },
        deadline: {
            type: Date
        },
        color: {
            type: String,
            default: '000'
        },
        disableInteraction: {
            type: Boolean,
            default: false
        },
        dark: {
            type: Boolean,
            required: false,
            default: false
        }
    })
</script>

<template>

    <router-link :to="{ path: 'forloeb-overview', query: { id: id } }" :class="{ 'disabled': props.disableInteraction }">

    <div :class="['card', 'course', {'dark': props.dark}]" ref="cardRef">
        <div :class="['card-header', {'pointer': !props.disableInteraction}]" @click="expandCard">

            <div class="card-titles">
                <p class="card-title">
                    {{ name != '' ? name :  'Forløb uden titel' }}
                </p>
                <p class="card-subtitle">
                    {{ title }}
                </p>
            </div>

            <div class="card-details">
                <div>
                    <div class="icon"><i class="fa-solid fa-clock"></i></div>
                    <div class="text">
                        <div class="small faded">Opstart</div>
                        <div>{{ startDate ? returnFormattedDate(startDate) : 'Ingen startdato' }}</div>
                    </div>
                </div>

                <div>
                    <div class="icon"><i class="fa-solid fa-clock"></i></div>
                    <div class="text">
                        <div class="small faded">Afslutning</div>
                        <div>{{ deadline ? returnFormattedDate(deadline) : 'Ingen deadline' }}</div>
                    </div>
                </div>
            </div>
            
        </div>

        <div class="card-content always-show"><ProgressBar :hideText="true" :percentage="5" /></div>
    </div>

    </router-link>

</template>