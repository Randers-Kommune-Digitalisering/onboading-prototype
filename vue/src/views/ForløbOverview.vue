
<script setup>
    import { useRoute } from 'vue-router'
    import CourseOverview from '@/components/CourseOverview.vue'
    import { getUserInfo } from '../services/keycloakService'
    import { ref } from 'vue'

    const route = useRoute()
    const id = parseInt(route.query.id || route.query.tid, 10)
    const isTemplate = route.query.tid !== undefined

    const adminView = ref(false)
    const ansvarligView = ref(false)
    const userInfo = ref(null)

    getUserInfo().then((response) => {
        userInfo.value = response
        if (!userInfo.value) {
            console.error('User info not found in response:', response)
            return
        }
        let userRoles = userInfo.value.roles
        if (userRoles) {
            adminView.value = userRoles.includes('Admin')
            ansvarligView.value = !adminView.value && userRoles.includes('Ansvarlig')
        } else {
            console.error('User roles not found in response:', response)
        }
    }).catch((error) => {
        console.error('Error fetching user info:', error)
    })
    
</script>

<template>
    <div>
        <CourseOverview v-if="userInfo != null && (adminView || ansvarligView)"
                        :id="id"
                        :showDetails="true"
                        :userInfo="userInfo"
                        :adminView="adminView"
                        :isTemplate="isTemplate" />
    </div>
</template>