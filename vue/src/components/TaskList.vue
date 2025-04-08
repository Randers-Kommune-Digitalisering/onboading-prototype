<script setup>
    import Card from './TaskItem.vue'

    const props = defineProps({
        tasks: {
            type: Array,
            required: false
        },
        adminView: {
            type: Boolean,
            default: false
        },
        title:
        {
            type: String,
            required: false
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
    <p :class="'indent-tiny bold uppercase p-header-adjust' + (largeHeaderAdjust ? '-large' : '')">{{ (title ?? (adminView ? 'Aktuelle' : 'Dine') + ' opgaver' ) }} </p>
    <div class="card-list" v-if="tasks && tasks.length > 0">
        <Card v-for="(task, index) in tasks"
            :adminView="adminView"
            :id="task.OpgaveID ?? task.OpgaveskabelonID"
            :title="task.title"
            :header="task.header ?? task.beskrivelse"
            :description="task.beskrivelse"
            :relativeStartdate="task.relativ_startdag"
            :relativeEnddate="task.relativ_slutdag"
            :startdate="task.startdato ? new Date(new Date(task.startdato)) : null"
            :deadline="task.slutdato ? new Date(new Date(task.slutdato)) : null"
            :responsible="task.ansvarlig"
            :booking="task.booking ? new Date(new Date(task.booking)) : null"
            :color="props.itemColor != null ? props.itemColor : (!templateView && new Date(task.slutdato) < new Date()) ? 'bf4e4e' : defaultItemColor"
            :expandByDefault="expandFirstItem && index == 0"
            :dark="dark"
            :templateView="templateView"
            :isTemplate="task.OpgaveskabelonID != null"
            :result="task.result"
            :ressources="task.resourcer" />
    </div><!-- /card-list -->
    <div v-else>
        <p class="indent-tiny">Ingen opgaver fundet.</p>
    </div>

</template>