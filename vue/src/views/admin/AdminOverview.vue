<script setup>
	import { ref, onMounted } from 'vue'
	import keycloak from '@/keycloak'

	import { getAllForloeb, getForloebByAdmin } from '../../services/forløbService'
	import { getOpgaverByForloebID } from '../../services/opgaveService'
	import CourseList from '@/components/CourseList.vue'

	const ongoingForloeb = ref([])
	const completedForloeb = ref([])

	const testData = [{'id': 1, 'title': 'Demo forløb 1', 'name': 'Soren T'},{'id': 1, 'title': 'Demo forløb 1', 'name': 'Soren T'}]

	onMounted(async () => {
		if (keycloak.authenticated) {
			const loggedInAdmin = keycloak.tokenParsed?.name || null
			
			if(!loggedInAdmin) {
				console.error("No admin name found")
				return
			}

			const headers =  { adminname: loggedInAdmin }
			const response = await getForloebByAdmin({headers})
			ongoingForloeb.value = response.data
		}
	})
</script>

<template>
  <CourseList :courses="ongoingForloeb" />
</template>