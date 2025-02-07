<script setup>
defineProps({
        percentage: {
            type: Number,
            required: true
        }
    })
</script>

<template>

    <p class="indent-tiny bold uppercase p-header-adjust">Fremskridt</p>
    <div class="progression-bar">
        <div class="progression" :style="`width: `+ percentage +`%`">{{ percentage }}%</div>
    </div>
    <p class="indent-tiny">{{ percentage == 100 ? 'Du har gennemført alle opgaver, godt arbejde!' :
                              percentage >= 80  ? 'Du har snart gennemført alle opgaver!' :
                              'Gennemfør opgaver for at opnå et højere fremskridt!' }}</p>

</template>