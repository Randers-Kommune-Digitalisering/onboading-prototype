<script setup>
	import { ref, onMounted, watch } from 'vue'
	import keycloak from '@/keycloak'

	import { getForloebsskabeloner } from '@/services/forløbsskabelonService'
	import { getOpgaveskabeloner } from '@/services/opgaveskabelonService'

	import CourseList from '@/components/CourseList.vue'
	import TaskList from '@/components/TaskList.vue' // Import TaskList component

	const TemplateType = {
		Forloebsskabelon: 0,
		Opgaveskabelon: 1
	}
	
	const forloebTemplates = ref([])
	const opgaveTemplates = ref([])
	const selectedType = ref(TemplateType.Forloebsskabelon)

	const fetchTemplates = async () => {
		if (keycloak.authenticated) {
			const loggedInAdmin = keycloak.tokenParsed?.name || null
			
			if(!loggedInAdmin) {
				console.error("No admin name found")
				return
			}

			const headers =  { adminname: loggedInAdmin }
			let response

			if (selectedType.value === TemplateType.Forloebsskabelon) {
				response = await getForloebsskabeloner({headers})
			} else {
				response = await getOpgaveskabeloner({headers})
			}

			if (response.data == null)
				return

			if (!Array.isArray(response.data))
				response.data = [response.data]

			if (selectedType.value === TemplateType.Forloebsskabelon)
				forloebTemplates.value = response.data
			else
				opgaveTemplates.value = response.data
		}
	}

	onMounted(fetchTemplates)
	watch(selectedType, fetchTemplates)
</script>

<template>
	<div class="navItems">
		<div @click="selectedType=TemplateType.Forloebsskabelon" :class="['navItem', {'selected': selectedType==TemplateType.Forloebsskabelon}]">
			<i class="fa-regular fa-calendar fa-xl"></i>
			<span>Forløbsskabeloner</span>
		</div>
		<div @click="selectedType=TemplateType.Opgaveskabelon" :class="['navItem', {'selected': selectedType==TemplateType.Opgaveskabelon}]">
			<i class="fa-solid fa-list-check fa-xl"></i>
			<span>Opgaveskabeloner</span>
		</div>
	</div>
    <p class="indent-tiny bold uppercase p-header-adjust">{{ selectedType==TemplateType.Forloebsskabelon ? 'Forløbsskabeloner' : 'Opgaveskabeloner' }}</p>
	<div class="buttons">
        <router-link v-if="selectedType==TemplateType.Forloebsskabelon" :to="`/create-forloebsskabelon`" class="button">+ Opret forløbsskabelon</router-link>
        <router-link v-if="selectedType==TemplateType.Opgaveskabelon" :to="`/create-opgaveskabelon`" class="button">+ Opret opgaveskabelon</router-link>
    </div>
  	<CourseList v-if="selectedType==TemplateType.Forloebsskabelon" :courses="forloebTemplates" title="" />
	<TaskList v-if="selectedType==TemplateType.Opgaveskabelon" :tasks="opgaveTemplates" title="" />
</template>

<style scoped>
.navItems {
	display: flex;
	justify-content: flex-start;
	margin-bottom: 1rem;
	gap: 0.6rem;
	border-bottom: 0.1rem solid var(--color-navbar-item-hover);
}
.navItems .navItem {
	background-color: var(--color-card-faded);
}
.navItems .navItem:hover {
	background-color: var(--color-card-dark);
}
.navItems .navItem.selected {
	background-color: var(--color-background);
	pointer-events: none;
	border-top: 0.1rem solid var(--color-navbar-item-hover);
	border-left: 0.1rem solid var(--color-navbar-item-hover);
	border-right: 0.1rem solid var(--color-navbar-item-hover);
	border-bottom-left-radius: 0;
	border-bottom-right-radius: 0;
	transform: translateY(0.1rem);
}
.navItems .navItem:not(.selected) {
	margin-bottom: 0.4rem;
}

@media only screen and (min-width: 768px) {
    .navItems {
        max-width: 38rem;
    }
}
</style>