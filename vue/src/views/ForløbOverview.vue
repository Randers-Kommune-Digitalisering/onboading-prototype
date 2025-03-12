
<script setup>
    import { useRoute } from 'vue-router'
    import CourseOverview from '@/components/CourseOverview.vue'

    const route = useRoute()
    const id = parseInt(route.query.id || route.query.tid, 10)
    const isTemplate = route.query.tid !== undefined
</script>

<template>
    <div>
        <!-- <p>URL Parameter ID: {{ id }}</p> -->
        <CourseOverview :id="id" :showDetails="true" :adminView="true" :isTemplate="isTemplate" />
    </div>
</template>