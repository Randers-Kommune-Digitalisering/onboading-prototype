<script setup>
	import { ref, onMounted } from 'vue'
	import keycloak from '@/keycloak'

	import { getForloebsskabeloner } from '@/services/forløbsskabelonService'
	import CourseList from '@/components/CourseList.vue'

	const TemplateType = {
		Forloebsskabelon: 0,
		Opgaveskabelon: 1
	}
	
	const templates = ref([])
	const selectedType = ref(TemplateType.Forloebsskabelon)

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
    <p class="indent-tiny bold uppercase p-header-adjust-medium">{{ selectedType==TemplateType.Forloebsskabelon ? 'Forløbsskabeloner' : 'Opgaveskabeloner' }}</p>
	<div class="buttons">
        <router-link v-if="selectedType==TemplateType.Forloebsskabelon" :to="`/create-forloebsskabelon`" class="button">+ Opret forløbsskabelon</router-link>
        <router-link v-if="selectedType==TemplateType.Opgaveskabelon" :to="`/create-opgaveskabelon`" class="button">+ Opret opgaveskabelon</router-link>
    </div>
  	<CourseList :courses="templates" title="" />
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