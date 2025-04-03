<script setup>
	import { ref, onMounted } from 'vue'

	import { getUserInfo } from '../../services/keycloakService.js'
	import { getForloebByAdmin } from '@/services/forløbService.js'
	import CourseList from '@/components/CourseList.vue'

	const forloeb_ongoing = ref([])
	const forloeb_future = ref([])
	const forloeb_completed = ref([])

	onMounted( () => {	
		getUserInfo().then(userInfo => {
			const loggedInAdmin = userInfo.email || 'No mail'

			if(!loggedInAdmin) {
					console.error("No admin mail found")
					return
				}

				const headers =  { adminmail: loggedInAdmin }
				getForloebByAdmin({headers}).then( response => {
					if (response.data == null)
						return

					if (!Array.isArray(response.data))
						response.data = [response.data]

					for (const item of response.data) {
						if (new Date(item.startdate) > new Date())
							forloeb_future.value.push(item)
						else
						if (new Date(item.enddate) < new Date())
							forloeb_completed.value.push(item)
						else 
							forloeb_ongoing.value.push(item)
					}

					// Sort and limit the number of completed courses
					forloeb_completed.value.sort((a, b) => new Date(b.enddate) - new Date(a.enddate))
					forloeb_completed.value = forloeb_completed.value.slice(0, 15)
				})

		}).catch(error => {
			console.error('Error fetching user info:', error);
		});
	})
</script>

<template>
  <CourseList :courses="forloeb_ongoing" />
  <CourseList :courses="forloeb_future" title="Kommende forløb" :largeHeaderAdjust="true" />
  <CourseList :courses="forloeb_completed" title="Afsluttede forløb" :largeHeaderAdjust="true" :dark="true" />
</template>