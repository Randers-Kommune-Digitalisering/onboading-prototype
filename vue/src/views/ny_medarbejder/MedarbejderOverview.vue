<script setup>
	import { ref, onMounted } from 'vue'

	import { getUserInfo } from '../../services/keycloakService.js'
	import CourseOverview from '@/components/CourseOverview.vue'

	const user = ref({})
	const isUserDataLoaded = ref(false)
  
	onMounted( () => {	
		getUserInfo().then(userInfo => {
			user.value = userInfo
			isUserDataLoaded.value = true
		}).catch(error => {
			console.error('Error fetching user info:', error)
		})
  	})
</script>

<template>
	<div v-if="isUserDataLoaded && user && user != {}">
		<CourseOverview :userInfo="user" />
	</div>
</template>