<script setup>
    import Card from './Card.vue'

    defineProps({
        taskList: {
            type: Array,
            required: false
        }
    })
</script>

<template>

    <p class="indent-tiny bold uppercase p-header-adjust-large">Dine opgaver</p>
    <div class="card-list" v-if="taskList && taskList.length > 0">
        <Card v-for="task in taskList"
            :id="'card_' + task.OpgaveID"
            :title="task.title"
            :header="task.header ?? task.beskrivelse"
            :description="task.beskrivelse"
            :deadline="new Date(new Date(task.slutdato).getTime() + 8 * 60 * 60 * 1000)"
            :responsible="task.ansvarlig"
            :booking="new Date(new Date(task.booking).getTime() + 6 * 60 * 60 * 1000)"
            image="https://www.teknologisk.dk/_/media/67761&w=1460&h=808&r=cover&_filename=67761_7-gode-rr%C3%A5d-til-IT-sikkerhed.jpg"
            color="4c4980"
            link=""
            isComplete="false" />
    </div><!-- /card-list -->
    <div v-else>
        <p class="indent-tiny">Ingen opgaver fundet.</p>
    </div>

</template>