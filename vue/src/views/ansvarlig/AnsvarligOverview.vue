<script setup>
    import { useRoute } from 'vue-router'
	import { ref} from 'vue'

	import { getUserInfo } from '@/services/keycloakService.js'
	import CourseOverview from '@/components/CourseOverview.vue'

    const route = useRoute()
	const userInfo = ref(null)

	getUserInfo().then(response => {
		userInfo.value = response
	}).catch(error => {
		console.error('Error fetching user info:', error)
	})
</script>

<template>
	<div v-if="userInfo && userInfo.email && userInfo.email != ''">
		<CourseOverview :ansvarligView="true" />
	</div>
</template>
