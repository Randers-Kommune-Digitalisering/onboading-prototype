<script setup>
    import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
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

    const listRef = ref(null)
    const frozenColumns = ref([])
    const isLayoutFrozen = ref(false)
    const frozenColumnWidth = ref(null)
    let freezeAnimationFrameId = 0

    const getTaskId = (task, index) => task.OpgaveID ?? task.OpgaveskabelonID ?? `task-${index}`

    const layoutItems = computed(() => {
        if (!props.tasks || props.tasks.length === 0)
            return []

        return props.tasks.flatMap((task, index) => {
            const taskId = getTaskId(task, index)
            const items = []

            if (props.forloebStartDate != null && index === props.startMessageIndex)
                items.push({ key: `start-spacer-${taskId}-${index}`, type: 'start-spacer' })

            items.push({ key: `task-${taskId}-${index}`, type: 'task', task })
            return items
        })
    })

    const taskListSignature = computed(() => layoutItems.value.map(item => item.key).join('|'))

    const findNearestColumnIndex = (columnLefts, left) => {
        let nearestIndex = 0
        let nearestDistance = Number.POSITIVE_INFINITY

        columnLefts.forEach((columnLeft, index) => {
            const distance = Math.abs(columnLeft - left)
            if (distance < nearestDistance) {
                nearestDistance = distance
                nearestIndex = index
            }
        })

        return nearestIndex
    }

    const resetFrozenLayout = () => {
        isLayoutFrozen.value = false
        frozenColumns.value = []
        frozenColumnWidth.value = null
    }

    const freezeCurrentLayout = async () => {
        await nextTick()

        if (!listRef.value || layoutItems.value.length === 0)
            return

        const itemNodes = Array.from(listRef.value.querySelectorAll('[data-layout-key]'))
        if (itemNodes.length === 0)
            return

        const itemsByKey = new Map(layoutItems.value.map(item => [item.key, item]))
        const measuredEntries = itemNodes.map(node => {
            const rect = node.getBoundingClientRect()
            return {
                key: node.getAttribute('data-layout-key'),
                left: Math.round(rect.left),
                top: rect.top
            }
        })

        const sortedLefts = [...new Set(measuredEntries.map(entry => entry.left).sort((a, b) => a - b))]
        const columnLefts = []
        const tolerancePx = 8

        sortedLefts.forEach((left) => {
            const previousLeft = columnLefts[columnLefts.length - 1]
            if (previousLeft == null || Math.abs(previousLeft - left) > tolerancePx)
                columnLefts.push(left)
        })

        if (columnLefts.length === 0)
            columnLefts.push(0)

        const measuredColumns = Array.from({ length: columnLefts.length }, () => [])

        measuredEntries
            .sort((a, b) => a.top - b.top || a.left - b.left)
            .forEach((entry) => {
                const item = itemsByKey.get(entry.key)
                if (!item)
                    return

                const columnIndex = findNearestColumnIndex(columnLefts, entry.left)
                measuredColumns[columnIndex].push(item)
            })

        frozenColumns.value = measuredColumns
        frozenColumnWidth.value = Math.round(itemNodes[0].getBoundingClientRect().width)
        isLayoutFrozen.value = true
    }

    const scheduleLayoutFreeze = () => {
        if (layoutItems.value.length === 0)
            return

        if (freezeAnimationFrameId)
            cancelAnimationFrame(freezeAnimationFrameId)

        freezeAnimationFrameId = requestAnimationFrame(() => {
            freezeAnimationFrameId = 0
            freezeCurrentLayout()
        })
    }

    watch(taskListSignature, () => {
        resetFrozenLayout()
        scheduleLayoutFreeze()
    })

    onMounted(() => {
        scheduleLayoutFreeze()
    })

    onBeforeUnmount(() => {
        if (freezeAnimationFrameId)
            cancelAnimationFrame(freezeAnimationFrameId)
    })

    const getTaskColor = (task) => {
        if (task.result)
            return completedItemColor

        if (!props.templateView && !props.isPreparation && new Date(task.slutdato) < new Date())
            return overdueItemColor

        if (!props.templateView && !props.isPreparation && new Date(task.startdato) > new Date())
            return upcomingItemColor

        if (task.hidden === true)
            return hiddenItemColor

        return defaultItemColor
    }

    const getTaskBorder = (task) => {
        if (!task.result && !props.templateView && !props.isPreparation && new Date(task.slutdato) < new Date())
            return overdueItemColor

        return task.hidden === true ? hiddenItemBorderColor : null
    }

    const buildCardProps = (task) => ({
        id: task.OpgaveID ?? task.OpgaveskabelonID,
        forloebId: task.ForløbID,
        username: task.name,
        title: task.title,
        header: task.header ?? task.beskrivelse,
        description: task.beskrivelse,
        note: task.note,
        group: task.gruppe,
        relativeStartdate: task.relativ_startdag,
        relativeEnddate: task.relativ_slutdag,
        startdate: task.startdato ? new Date(new Date(task.startdato)) : null,
        deadline: task.slutdato ? new Date(new Date(task.slutdato)) : null,
        ansvarlig: task.ansvarlig,
        ansvarligEmail: task.ansvarligEmail,
        booking: task.booking ? new Date(new Date(task.booking)) : null,
        hidden: task.hidden === true,
        color: getTaskColor(task),
        border: getTaskBorder(task),
        scrollTo: props.scrollToItem === task.OpgaveID || props.scrollToItem === task.OpgaveskabelonID,
        dark: props.dark || task.result,
        templateView: props.templateView,
        isTemplate: task.OpgaveskabelonID != null,
        result: task.result,
        ressources: task.resourcer,
        mails: task.pending_emails,
        sentMails: task.sent_emails,
        isPreparation: props.isPreparation,
        external: props.external,
        accessKey: props.accessKey
    })
</script>

<template>
    <div>
        <p :class="'indent-tiny bold uppercase p-header-adjust' + (largeHeaderAdjust ? '-large' : '')">{{ (title ?? 'Opgaver' ) }} </p>
        <div class="card-list row" ref="listRef" v-if="tasks && tasks.length > 0 && !isLayoutFrozen">
            <template v-for="item in layoutItems" :key="`measure-${item.key}`">
                <div class="start-spacer" :data-layout-key="item.key" v-if="item.type === 'start-spacer'">
                    <div class="line"></div>
                    <span class="text">Forløbet starter
                        {{
                            isPreparation || templateView ? 'her' :
                            new Date(forloebStartDate).toLocaleDateString('da-DK', { year: 'numeric', month: '2-digit', day: '2-digit' })
                        }}
                    </span>
                </div>
                <Card
                    :data-layout-key="item.key"
                    v-else
                    v-bind="buildCardProps(item.task)"
                    @result-updated="onTaskResultUpdated" />
            </template>
        </div><!-- /card-list -->
        <div class="task-grid" v-else-if="tasks && tasks.length > 0">
            <div class="task-grid-column"
                 v-for="(column, columnIndex) in frozenColumns"
                 :key="`column-${columnIndex}`"
                 :style="frozenColumnWidth ? { width: `${frozenColumnWidth}px` } : null">
                <template v-for="item in column" :key="`frozen-${item.key}`">
                    <div class="start-spacer" v-if="item.type === 'start-spacer'">
                        <div class="line"></div>
                        <span class="text">Forløbet starter
                            {{
                                isPreparation || templateView ? 'her' :
                                new Date(forloebStartDate).toLocaleDateString('da-DK', { year: 'numeric', month: '2-digit', day: '2-digit' })
                            }}
                        </span>
                    </div>
                    <Card
                        v-else
                        v-bind="buildCardProps(item.task)"
                        @result-updated="onTaskResultUpdated" />
                </template>
            </div>
        </div>
        <div v-else>
            <p class="indent-tiny" v-if="isFetchingTasks">Indlæser ...</p>
            <p class="indent-tiny faded" v-else>Ingen opgaver fundet.</p>
        </div>
    </div>

</template>
<style scoped>
.task-grid {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    width: 100%;
    overflow-x: auto;
}

.task-grid-column {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    min-width: 0;
}

.task-grid-column > * {
    width: 100%;
}

.task-grid-column > .card.task {
    max-width: 100%;
}

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