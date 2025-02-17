<script setup>
defineProps({
        percentage: {
            type: Number,
            required: true
        },
        hideText: {
            type: Boolean,
            default: false
        }
    })
</script>

<template>

    <p v-if="!hideText" class="indent-tiny bold uppercase p-header-adjust">Fremskridt</p>
    <div class="progression-bar">
        <div class="progression" :style="`width: `+ percentage +`%`">{{ percentage }}%</div>
    </div>
    <p v-if="!hideText" class="indent-tiny">{{ percentage == 100 ? 'Du har gennemført alle opgaver, godt arbejde!' :
                              percentage >= 80  ? 'Du har snart gennemført alle opgaver!' :
                              'Gennemfør opgaver for at opnå et højere fremskridt!' }}</p>

</template>