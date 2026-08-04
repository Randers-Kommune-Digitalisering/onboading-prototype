<script setup>
defineProps({
    userFullName: {
        type: String,
        required: true
    },
    userRole: {
        type: String,
        required: true
    },
    text: {
        type: String
    }
})
</script>

<template>
    <p class="indent-tiny bold uppercase p-header-adjust">Introduktion</p>

    <p class="large indent-tiny">Velkommen som {{ userRole.toLowerCase() }}, {{ userFullName }}!</p>
    <p class="indent-tiny">{{ text }}</p>
</template>