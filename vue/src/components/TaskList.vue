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
        },
        forloebStartDate:
        {
            type: Date,
            default: null
        },
        startMessageIndex:
        {
            type: Number,
            default: -1
        }
    })

    const defaultItemColor = '4c4980'
</script>

<template>
    <div>
        <p :class="'indent-tiny bold uppercase p-header-adjust' + (largeHeaderAdjust ? '-large' : '')">{{ (title ?? 'Opgaver' ) }} </p>
        <div class="card-list" v-if="tasks && tasks.length > 0">
            <template v-for="(task, index) in tasks">
                <div class="start-spacer" v-if="forloebStartDate != null && index === startMessageIndex">
                    <div class="line"></div>
                    <span class="text">Forløbet starter {{ new Date(forloebStartDate).toLocaleDateString('da-DK', { year: 'numeric', month: '2-digit', day: '2-digit' }) }}</span>
                </div>
                <Card
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
                    :color="props.itemColor != null ? props.itemColor : task.result ? '617a5d' : (!templateView && new Date(task.slutdato) < new Date()) ? 'bf4e4e' : defaultItemColor"
                    :border="(!task.result && !templateView && new Date(task.slutdato) < new Date()) ? 'bf4e4e' : null"
                    :expandByDefault="expandFirstItem && index == 0 || expandItem === task.OpgaveID || expandItem === task.OpgaveskabelonID"
                    :dark="dark || task.result"
                    :templateView="templateView"
                    :isTemplate="task.OpgaveskabelonID != null"
                    :result="task.result"
                    :ressources="task.resourcer"
                    :mails="task.pending_emails" />
            </template>
        </div><!-- /card-list -->
        <div v-else>
            <p class="indent-tiny" v-if="isFetchingTasks">Indlæser ...</p>
            <p class="indent-tiny" v-else>Ingen opgaver fundet.</p>
        </div>
    </div>

</template>
<style scoped>
.start-spacer {
    font-size: 0.8em;
    text-transform: none;
    width: 100%;
    max-width: 38rem;
    text-align: center;
    position: relative;
}
    .start-spacer > .line {
        background-color: var(--color-card-dark);
        height: 0.2rem;
        position: absolute;
        top: 50%;
        width: 100%;
        max-width: 38rem;
        z-index: 1;
    }
    .start-spacer > .text {
        background-color: var(--color-background);
        padding: 0 0.5rem;
        position: relative;
        z-index: 2;
        width: auto;
    }
</style>