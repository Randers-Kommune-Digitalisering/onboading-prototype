
<script setup>
    import { useRoute } from 'vue-router'
    import ForloebOverview from '@/components/CourseOverview.vue'

    const route = useRoute()
    const id = route.query.id
</script>

<template>
    <div>
        <p>URL Parameter ID: {{ id }}</p>
    </div>
</template>