<script setup>
	import { ref, onMounted } from 'vue'
	import keycloak from '@/keycloak'

	import { getForloebsskabeloner } from '@/services/forløbskabelonService'
	import CourseList from '@/components/CourseList.vue'

	const templates = ref([])

	onMounted(async () => {
		if (keycloak.authenticated) {
			const loggedInAdmin = keycloak.tokenParsed?.name || null
			
			if(!loggedInAdmin) {
				console.error("No admin name found")
				return
			}

			const headers =  { adminname: loggedInAdmin }
			const response = await getForloebsskabeloner({headers})

			if (response.data == null)
				return

			if (!Array.isArray(response.data))
				response.data = [response.data]

			templates.value = response.data
		}
	})
</script>

<template>
	<div class="buttons">
        <router-link :to="`/create-forloebsskabelon`" class="button">+ Opret forløbsskabelon</router-link>
    </div>
  <CourseList :courses="templates" title="Skabeloner" />
</template>