
<script setup>
    import { useRoute } from 'vue-router'
    import CourseOverview from '@/components/CourseOverview.vue'

    const route = useRoute()
    const id = route.query.id
</script>

<template>
    <div>
        <!-- <p>URL Parameter ID: {{ id }}</p> -->
        <CourseOverview :id="id" :showDetails="true" :adminView="true" />
    </div>
</template>