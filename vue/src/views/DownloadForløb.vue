
<script setup>
    import { ref, onMounted } from 'vue'
    import { useRoute } from 'vue-router'

    const route = useRoute()
    const id = parseInt(route.query.id, 10)

    import { getForloebById } from '@/services/forløbService.js'
    import { getOpgaverByForloebID } from '@/services/opgaveService.js'

    const forloeb = ref(null)
    const opgaver = ref([])

    onMounted(() => {
        getForloebById(id).then((response) => {
            forloeb.value = response.data

        }).catch((error) => {
            console.error('Error fetching forløb data:', error)
        })

        getOpgaverByForloebID(id).then((response) => {
            opgaver.value = response.data
            opgaver.value.sort((a, b) => new Date(a.startdato) - new Date(b.startdato))
        }).catch((error) => {
            console.error('Error fetching opgaver data:', error)
        })
    })

    const formatDate = (dateString) => {
        const options = { year: 'numeric', month: '2-digit', day: '2-digit' }
        return new Date(dateString).toLocaleDateString('da-DK', options)
    }
</script>

<template>
    <div class="forloeb-details">
        <div v-if="forloeb != null && opgaver != null">
            <p class="header">{{ forloeb.name }}</p>
            <p class="faded">Onboardingforløb med start d. {{ formatDate(forloeb.startdate) }}</p>

            <div v-for="opgave in opgaver" class="opgave">
                <p class="faded">{{ formatDate(opgave.startdato) }}</p>
                <p class="title">{{ opgave.title }}</p>
                <p>{{ opgave.beskrivelse }}</p>
                <p v-if="opgave.ansvarlig != ''">
                    <span class="faded">Ansvarlig:</span> {{ opgave.ansvarlig }}
                    (<a :href="'mailto:' + opgave.ansvarligEmail">{{ opgave.ansvarligEmail }}</a>)
                </p>
                <p v-if="opgave.resourcer.length > 0" class="faded">Ressourcer: 
                    <span v-for="resource in opgave.resourcer" :key="resource.id">
                        <a :href="resource.url" target="_blank">
                            {{ resource.name }}{{ opgave.resourcer.length - 1 !== opgave.resourcer.indexOf(resource) ? ', ' : '' }}
                        </a>
                    </span>
                </p>
            </div>
        </div>
    </div>
</template>

<style scoped>
    .forloeb-details {
        width: 100%;
        height: 100%;
        min-height: 100dvh;
        background-color: white;
        padding: 2rem;
    }
    .header {
        font-size: 2em;
        font-weight: bold;
        margin-bottom: 0rem;
    }
    .opgave {
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        background-color: #f9f9f9;
        border: 0.1rem solid #e0e0e0;
        /* box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); */
    }
    .opgave + .opgave {
        margin-top: 1rem;
    }
    .title {
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 0.5rem;
        margin-top: 0rem;
    }
    .faded {
        color: #888;
        margin-bottom: 0.5rem;
    }
    .faded + .title {
        margin-top: 0rem;
    }
    .header + .faded {
        margin-top: 0rem;
        margin-bottom: 2rem;
    }
    a {
        color: #007bff;
        text-decoration: none;
    }
</style>