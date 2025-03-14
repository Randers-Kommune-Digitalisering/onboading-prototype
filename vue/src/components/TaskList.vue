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
    <p :class="'indent-tiny bold uppercase p-header-adjust' + (adminView || largeHeaderAdjust ? '-large' : '')">{{ (title ? title : ( adminView ? 'Aktuelle' : 'Dine') + ' opgaver' ) }} </p>
    <div class="card-list" v-if="tasks && tasks.length > 0">
        <Card v-for="(task, index) in tasks"
            :adminView="adminView"
            :id="task.OpgaveID"
            :title="task.title"
            :header="task.header ?? task.beskrivelse"
            :description="task.beskrivelse"
            :relativeStartdate="task.relativ_startdag"
            :relativeEnddate="task.relativ_slutdag"
            :startdate="new Date(new Date(task.startdato))"
            :deadline="new Date(new Date(task.slutdato))"
            :responsible="task.ansvarlig"
            :booking="new Date(new Date(task.booking))"
            image="https://www.teknologisk.dk/_/media/67761&w=1460&h=808&r=cover&_filename=67761_7-gode-rr%C3%A5d-til-IT-sikkerhed.jpg"
            :color="props.itemColor != null ? props.itemColor : new Date(new Date(task.slutdato).getTime() + 8 * 60 * 60 * 1000) < new Date() ? 'bf4e4e' : defaultItemColor"
            isComplete="false"
            :expandByDefault="expandFirstItem && index == 0"
            :dark="dark"
            :templateView="templateView"
            :result="task.result" />
    </div><!-- /card-list -->
    <div v-else>
        <p class="indent-tiny">Ingen opgaver fundet.</p>
    </div>

</template>