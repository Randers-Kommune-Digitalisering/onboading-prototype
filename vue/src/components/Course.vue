<script setup>
    import { ref } from 'vue'
    import ProgressBar from './ProgressBar.vue'
    var cardRef = ref(null)

    const expandCard = () => {
        cardRef.value.classList.toggle('expand-content')
    }

    const returnTimeLeft = (deadline) => {
        const now = new Date()
        const diff = deadline - now
        const hours = Math.floor(diff / 1000 / 60 / 60)
        return hours
    }

    const returnFormattedDate = (date) => {
        const d = new Date(date)
        return d.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit' }) + ' ' + d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
    }

    defineProps({
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
        }
    })
</script>

<template>

    <div class="card course expand-content" ref="cardRef">
        <div class="card-header">
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

        <div class="card-content">
            <ProgressBar :hideText="true" :percentage="5" />
            <!--div class="buttons">
                <div class="button" v-if="link">Gå til kursus</div>
                <div class="button disabled">Markér gennemført</div>
            </div-->
        </div>
    </div>

</template>