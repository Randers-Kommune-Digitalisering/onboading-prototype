
<script setup>
    import { useRoute } from 'vue-router'
    import CourseOverview from '@/components/CourseOverview.vue'
    import { getUserInfo } from '@/services/keycloakService.js'
    import { ref } from 'vue'

    const route = useRoute()
    const id = parseInt(route.query.id || route.query.tid, 10)
    const isTemplate = route.query.tid !== undefined
	const _expandItem = route.query.item
	const expandItem = ref(_expandItem ? parseInt(_expandItem) : null)
    const userInfo = ref(null)

    getUserInfo().then((response) => {
        userInfo.value = response
    }).catch((error) => {
        console.error('Error fetching user info:', error)
    })
    
</script>

<template>
    <div>
        <CourseOverview v-if="userInfo != null && (userInfo.isAdmin || userInfo.isAnsvarlig)"
                        :id="id"
                        :showDetails="true"
                        :isTemplate="isTemplate"
                        :expandItem="expandItem" />
    </div>
</template>