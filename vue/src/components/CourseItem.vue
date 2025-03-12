<script setup>
    import { ref, onMounted } from 'vue'
    import ProgressBar from './ProgressBar.vue'

    import { getOpgaverByForloebID } from '@/services/opgaveService'

    const cardRef = ref(null)
    const completedPercentage = ref(0)

    const returnFormattedDate = (date) => {
        const d = new Date(date)
        return d.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit' }) // + ' ' + d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
    }

    const props = defineProps({
        id: {
            type: Number,
            required: true
        },
        tid: {
            type: Number,
            required: false
        },
        title: {
            type: String,
            required: true
        },
        name: {
            type: String
        },
        duration: {
            type: Number
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
        },
        tasks: {
            type: Array,
            required: false
        }
    })

    const opgaver = ref([])
    const isTemplate = props.id == null

    onMounted(() => {
        try {
            getOpgaverByForloebID(props.id)
            .then(response => {
                if (response?.data != null)
                {
                    opgaver.value = response.data
                    completedPercentage.value = opgaver.value.length > 0 ? Math.round((opgaver.value.filter(opgave => opgave.result).length / opgaver.value.length) * 100) : 0
                }
                else
                    opgaver.value = []
            })
        }
        catch (error) {
            console.log(error)
            opgaver.value = []
        }
    })

</script>

<template>
    <router-link :to="{ path: 'forloeb-overview', query: { id: id, tid: tid } }" :class="{ 'disabled': props.disableInteraction }">

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

            <div class="card-details" v-if="props.duration == null">
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
            <div class="card-details" v-else>
                <div>
                    <div class="icon"><i class="fa-solid fa-clock"></i></div>
                    <div class="text">
                        <div class="small faded">Varighed</div>
                        <div>{{ duration }} dage</div>
                    </div>
                </div>
            </div>
            
        </div>

        <div class="card-content always-show" v-if="!duration"><ProgressBar :hideText="true" :percentage="completedPercentage" /></div>
    </div>

    </router-link>

</template>