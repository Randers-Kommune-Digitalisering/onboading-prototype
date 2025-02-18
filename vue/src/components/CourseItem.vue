<script setup>
    import { ref } from 'vue'
    import ProgressBar from './ProgressBar.vue'
    var cardRef = ref(null)

    const expandCard = () => {
        if (!props.disableInteraction)
            cardRef.value.classList.toggle('expand-content')
    }

    const returnFormattedDate = (date) => {
        const d = new Date(date)
        return d.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit' }) + ' ' + d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
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
            type: String,
            default: ''
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

    <div :class="'card course ' + (props.dark ? 'dark' : '')" ref="cardRef">
        <div :class="'card-header ' + (!props.disableInteraction ? 'pointer' : '')" @click="expandCard">
            <div class="card-icon">
                <div :style="`background-color: #`+ color +`;`">
                    <div>{{ name[0].toLowerCase() }}</div>
                </div>
            </div>

            <div class="card-titles">
                <p class="card-title">
                    {{ name }}
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
        <div class="card-content">
            <div class="buttons">
                <div :class="'button disabled ' + (props.dark ? 'dark' : '')">+ Opret opgave</div>
                <router-link v-if="!props.disableInteraction" :to="{ path: 'forloeb-overview', query: { id: id } }" class="button">Se detaljer</router-link>
            </div>
        </div>
    </div>

</template>