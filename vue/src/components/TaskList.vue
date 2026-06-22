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
        scrollToItem:
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
        forloebStartDate:
        {
            type: Date,
            default: null
        },
        startMessageIndex:
        {
            type: Number,
            default: -1
        },
        isPreparation:
        {
            type: Boolean,
            default: false
        },
        external: {
            type: Boolean,
            default: false,
        },
        accessKey: {
            type: String,
            default: null,
        }
    })

    const emit = defineEmits(['task-result-change'])

    const onTaskResultUpdated = (payload) => {
        emit('task-result-change', payload)
    }

    const defaultItemColor = '4c4980'
    const completedItemColor = '617a5d'
    const overdueItemColor = 'bf4e4e'
    const upcomingItemColor = '777371'
    const hiddenItemColor = 'fcb103'
    const hiddenItemBorderColor = '9b9b9b'
</script>

<template>
    <div>
        <p :class="'indent-tiny bold uppercase p-header-adjust' + (largeHeaderAdjust ? '-large' : '')">{{ (title ?? 'Opgaver' ) }} </p>
        <div class="card-list row" v-if="tasks && tasks.length > 0">
            <template v-for="(task, index) in tasks">
                <div class="start-spacer" v-if="forloebStartDate != null && index === startMessageIndex">
                    <div class="line"></div>
                    <span class="text">Forløbet starter
                        {{
                            isPreparation || templateView ? 'her' :
                            new Date(forloebStartDate).toLocaleDateString('da-DK', { year: 'numeric', month: '2-digit', day: '2-digit' })
                        }}
                    </span>
                </div>
                <Card
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
                    :hidden="task.hidden === true"
                    :color="(task.result ? completedItemColor : (!templateView && !isPreparation && new Date(task.slutdato) < new Date()) ? overdueItemColor : (!templateView && !isPreparation && new Date(task.startdato) > new Date()) ? upcomingItemColor : task.hidden === true ? hiddenItemColor : defaultItemColor)"
                    :border="((!task.result && !templateView && !isPreparation && new Date(task.slutdato) < new Date()) ? overdueItemColor : task.hidden === true ? hiddenItemBorderColor : null)"
                    :scrollTo="scrollToItem === task.OpgaveID || scrollToItem === task.OpgaveskabelonID"
                    :dark="dark || task.result"
                    :templateView="templateView"
                    :isTemplate="task.OpgaveskabelonID != null"
                    :result="task.result"
                    :ressources="task.resourcer"
                    :mails="task.pending_emails"
					:isPreparation="isPreparation"
					:external="external"
                    :accessKey="accessKey"
                    @result-updated="onTaskResultUpdated" />
            </template>
        </div><!-- /card-list -->
        <div v-else>
            <p class="indent-tiny" v-if="isFetchingTasks">Indlæser ...</p>
            <p class="indent-tiny faded" v-else>Ingen opgaver fundet.</p>
        </div>
    </div>

</template>
<style scoped>
.start-spacer {
    font-size: 0.8em;
    text-transform: none;
    width: 100%;
    text-align: center;
    position: relative;
}
    .start-spacer > .line {
        background-color: var(--color-card-dark);
        height: 0.2rem;
        position: absolute;
        top: 50%;
        width: 100%;
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