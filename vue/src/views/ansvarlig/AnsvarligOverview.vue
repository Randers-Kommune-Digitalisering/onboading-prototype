<script setup>
    import { useRoute } from 'vue-router'
	import { ref} from 'vue'

	import { getUserInfo } from '@/services/keycloakService.js'
	import CourseOverview from '@/components/CourseOverview.vue'

    const route = useRoute()
	const userInfo = ref(null)
	const _expandItem = route.query.item
	const expandItem = ref(_expandItem ? parseInt(_expandItem) : null)

	getUserInfo().then(response => {
		userInfo.value = response
	}).catch(error => {
		console.error('Error fetching user info:', error)
	})
</script>

<template>
	<div v-if="userInfo && userInfo.email && userInfo.email != '' && userInfo.isAnsvarlig">
		<CourseOverview :ansvarligView="true" :expandItem="expandItem" />
	</div>
</template>