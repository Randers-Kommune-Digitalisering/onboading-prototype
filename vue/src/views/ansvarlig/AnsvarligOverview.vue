<script setup>
	import { ref} from 'vue'

	import { getUserInfo } from '@/services/keycloakService.js'
	import CourseOverview from '@/components/CourseOverview.vue'

	const userInfo = ref(null)

	getUserInfo().then(response => {
		if (!userInfo) {
			console.error('User info not found in response:', response)
			return
		}
		userInfo.value = response
	}).catch(error => {
		console.error('Error fetching user info:', error)
	})
</script>

<template>
	<div v-if="userInfo && userInfo.email && userInfo.email != ''">
		<CourseOverview :userInfo="userInfo" :ansvarligView="true" />
	</div>
</template>