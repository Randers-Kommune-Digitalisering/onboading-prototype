<script setup>
    import Card from './TaskItem.vue'

    const props = defineProps({
        tasks: {
            type: Array
        },
        isFetchingTasks: {
            type: Boolean,
            default: false
        },
        isFetchingTasksError: {
            type: Boolean,
            default: false
        },
        userInfo : {
            type: Object,
            required: true
        },
        username: {
            type: String,
            default: null
        },
        title:
        {
            type: String
        },
        largeHeaderAdjust:
        {
            type: Boolean,
            default: false
        },
        expandFirstItem:
        {
            type: Boolean,
            default: true
        },
        expandItem:
        {
            type: Number,
            default: null
        },
        dark:
        {
            type: Boolean,
            default: false
        },
        templateView:
        {
            type: Boolean,
            default: false
        },
        itemColor:
        {
            type: String
        }
    })

    const defaultItemColor = '4c4980'
</script>

<template>
    <p :class="'indent-tiny bold uppercase p-header-adjust' + (largeHeaderAdjust ? '-large' : '')">{{ (title ?? 'Opgaver' ) }} </p>
    <div class="card-list" v-if="tasks && tasks.length > 0">
        <Card v-for="(task, index) in tasks"
            :userInfo="userInfo"
            :id="task.OpgaveID ?? task.OpgaveskabelonID"
            :forloebId="task.ForløbID"
            :username="task.name"
            :title="task.title"
            :header="task.header ?? task.beskrivelse"
            :description="task.beskrivelse"
            :note="task.note"
            :group="task.gruppe"
            :relativeStartdate="task.relativ_startdag"
            :relativeEnddate="task.relativ_slutdag"
            :startdate="task.startdato ? new Date(new Date(task.startdato)) : null"
            :deadline="task.slutdato ? new Date(new Date(task.slutdato)) : null"
            :ansvarlig="task.ansvarlig"
            :ansvarligEmail="task.ansvarligEmail"
            :booking="task.booking ? new Date(new Date(task.booking)) : null"
            :color="props.itemColor != null ? props.itemColor : (!templateView && new Date(task.slutdato) < new Date()) ? 'bf4e4e' : defaultItemColor"
            :expandByDefault="expandFirstItem && index == 0 || expandItem === task.OpgaveID || expandItem === task.OpgaveskabelonID"
            :dark="dark"
            :templateView="templateView"
            :isTemplate="task.OpgaveskabelonID != null"
            :result="task.result"
            :ressources="task.resourcer" />
    </div><!-- /card-list -->
    <div v-else>
        <p class="indent-tiny" v-if="isFetchingTasks">Indlæser ...</p>
        <p class="indent-tiny" v-else>Ingen opgaver fundet.</p>
    </div>

</template>