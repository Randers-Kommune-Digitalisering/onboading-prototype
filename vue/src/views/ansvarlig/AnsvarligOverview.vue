<script setup>
    import { useRoute } from 'vue-router'
	import { ref} from 'vue'

	import { getUserInfo } from '@/services/keycloakService.js'
	import CourseOverview from '@/components/CourseOverview.vue'

    const route = useRoute()
	const userInfo = ref(null)
	const _scrollTo = route.query.item
	const scrollTo = ref(_scrollTo ? parseInt(_scrollTo) : null)

	getUserInfo().then(response => {
		userInfo.value = response
	}).catch(error => {
		console.error('Error fetching user info:', error)
	})
</script>

<template>
	<div v-if="userInfo && userInfo.email && userInfo.email != ''">
		<CourseOverview :ansvarligView="true" :scrollTo="scrollTo" />
	</div>
</template>
