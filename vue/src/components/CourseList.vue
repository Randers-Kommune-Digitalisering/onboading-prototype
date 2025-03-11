<script setup>
    import Card from './CourseItem.vue'

    defineProps({
        courses: {
            type: Array,
            required: false
        },
        title:
        {
            type: String,
            default: "Aktuelle forløb"
        }
    })
</script>

<template>

    <p class="indent-tiny bold uppercase p-header-adjust">{{ title }}</p>
    <div class="card-list" v-if="courses && courses.length > 0">
        <Card v-for="course in courses"
            :id="course.ForløbID"
            :title="course.usermail ?? course.privateEmail"
            :name="course.name"
            :startDate="new Date(course.startdate)"
            :deadline="new Date(course.enddate)"
            :duration="course.duration"
            color="4c4980" />
    </div>
    <div v-else>
        <p class="indent-tiny">Ingen forløb fundet.</p>
    </div>

</template>