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
        },
        largeHeaderAdjust:
        {
            type: Boolean,
            default: false
        },
        dark:
        {
            type: Boolean,
            default: false
        },
        color:
        {
            type: String,
            default: null
        }
    })
</script>

<template>
    <p :class="'indent-tiny bold uppercase p-header-adjust' + (largeHeaderAdjust ? '-large' : '')">{{ title ?? "Aktuelle forløb" }}</p>
    <div class="card-list" v-if="courses && courses.length > 0">
        <Card v-for="course in courses"
            :id="course.ForløbID"
            :tid="course.ForløbsskabelonID"
            :title="course.userdq != '' ? course.userdq : course.usermail"
            :name="course.name"
            :startDate="new Date(course.startdate)"
            :deadline="new Date(course.enddate)"
            :duration="course.varighed"
            :dark="dark"
            :isPreparation="course.isPreparation" />
    </div>
    <div v-else>
        <p class="indent-tiny faded">Ingen forløb fundet.</p>
    </div>

</template>