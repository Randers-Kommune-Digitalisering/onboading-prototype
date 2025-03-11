<script setup>
	import { ref, onMounted } from 'vue'
	import keycloak from '@/keycloak'

	import { getForloebByAdmin } from '@/services/forløbService'
	import CourseList from '@/components/CourseList.vue'

	const forloeb_ongoing = ref([])
	const forloeb_completed = ref([])

	onMounted(async () => {
		if (keycloak.authenticated) {
			const loggedInAdmin = keycloak.tokenParsed?.name || null
			
			if(!loggedInAdmin) {
				console.error("No admin name found")
				return
			}

			const headers =  { adminname: loggedInAdmin }
			const response = await getForloebByAdmin({headers})

			if (response.data == null)
				return

			if (!Array.isArray(response.data))
				response.data = [response.data]

			for (const item of response.data) {
				if (item.enddate < new Date())
					forloeb_completed.value.push(item)
				else 
					forloeb_ongoing.value.push(item)
			}

			// Sort and limit the number of completed courses
			forloeb_completed.value.sort((a, b) => new Date(b.enddate) - new Date(a.enddate))
			forloeb_completed.value = forloeb_completed.value.slice(0, 15)
		}
	})
</script>

<template>
  <CourseList :courses="forloeb_ongoing" />
  <CourseList :courses="forloeb_completed" title="Afsluttede forløb" />
</template>