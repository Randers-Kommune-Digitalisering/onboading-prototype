<script setup>
    import Card from './Course.vue'

    defineProps({
        courses: {
            type: Array,
            required: false
        }
    })
</script>

<template>

    <p class="indent-tiny bold uppercase p-header-adjust">Aktuelle forløb</p>
    <div class="card-list" v-if="courses && courses.length > 0">
        <Card v-for="course in courses"
            :title="course.title"
            :name="course.name"
            color="4c4980" />
    </div>
    <div v-else>
        <p class="indent-tiny">Ingen forløb fundet.</p>
    </div>

</template>