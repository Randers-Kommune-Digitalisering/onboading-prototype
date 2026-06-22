<script setup>
    import { ref, onMounted, watch } from 'vue'
    import ProgressBar from './ProgressBar.vue'

    import { getOpgaverByForloebID, getOpgaverByForloebsskabelonID } from '@/services/opgaveService.js'

    const completedPercentage = ref(0)

    const returnFormattedDate = (date) => {
        const d = new Date(date)
        return d.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit' }) // + ' ' + d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
    }

    const props = defineProps({
        id: {
            type: Number
        },
        tid: {
            type: Number
        },
        title: {
            type: String
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
        disableInteraction: {
            type: Boolean,
            default: false
        },
        dark: {
            type: Boolean,
            default: false
        },
        tasks: {
            type: Array
        },
        isPreparation: {
            type: Boolean,
            default: false
        }
    })

    const isTemplate = props.id == null
    const opgaver = ref(props.tasks || null)
    const hasForloebStarted = props.startDate && new Date(props.startDate) <= new Date()

    const updateCompletedPercentage = (tasks) => {
        completedPercentage.value = tasks?.length > 0
            ? Math.round((tasks.filter(opgave => opgave.result).length / tasks.length) * 100)
            : 0
    }

    watch(
        () => props.tasks,
        (tasks) => {
            if (tasks != null)
                updateCompletedPercentage(tasks)
        },
        { deep: true, immediate: true }
    )

    watch(
        () => opgaver.value,
        (tasks) => {
            if (props.tasks == null)
                updateCompletedPercentage(tasks)
        },
        { deep: true }
    )

    onMounted(async () => {
        try {
            if (props.tasks == null)
            {
                if (isTemplate)
                    getOpgaverByForloebsskabelonID(props.tid)
                    .then(response => {
                        if (response?.data != null)
                            opgaver.value = response.data
                    })
                else
                    getOpgaverByForloebID(props.id)
                    .then(response => {
                        if (response?.data != null)
                            opgaver.value = response.data
                    })
            }
        }
        catch (error) {
            console.error(error)
        }
    })

    const returnOpgaveOrOpgaver = (num) => {
        return num > 1 || num == 0 ? 'opgaver' : 'opgave'
    }

</script>

<template>

    <component
        :is="props.disableInteraction ? 'div' : 'router-link'"
        v-bind="!props.disableInteraction ? { to: { path: 'forloeb-overview', query: { id: id, tid: tid } } } : {}"
    >

    <div :class="['card', 'course', {'dark': props.dark}]">
        <div :class="['card-header', {'pointer': !props.disableInteraction}]">

            <div class="card-titles">
                <p class="card-title">
                    <span>{{ name != '' ? name :  'Forløb uden titel' }}</span>
                    <div class="tag" v-if="props.isPreparation">Under forberedelse</div>
                    <div class="tag gray" v-if="isTemplate">Skabelon</div>
                </p>
                <p v-if="title" class="card-subtitle">
                    {{ title }}
                </p>
            </div>

            <div class="card-details" v-if="!isTemplate && !isPreparation">

                <div>
                    <div class="icon"><i class="fa-regular fa-clock"></i></div>
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
                    <div class="icon"><i class="fa-solid fa-list-check"></i></div>
                    <div class="text">
                        <div class="small faded">Antal opgaver</div>
                        <div>{{ props.tasks?.length || opgaver?.length || 0 }} {{returnOpgaveOrOpgaver(props.tasks?.length || opgaver?.length || 0)}}</div>
                    </div>
                </div>
                <div>
                    <div class="icon"><i class="fa-solid fa-clock"></i></div>
                    <div class="text">
                        <div class="small faded">Varighed</div>
                        <div>{{ duration }} dag{{ duration > 0 ? 'e' : '' }}</div>
                    </div>
                </div>
            </div>
            
        </div>

        <div class="card-content always-show" v-if="!isTemplate && !isPreparation && hasForloebStarted">
            <ProgressBar :hideText="true" :percentage="completedPercentage" />
        </div>
    </div>

    </component>

</template>
