<script setup>
	import { ref, onMounted, watch } from 'vue'
	import { useRoute, useRouter } from 'vue-router'

	import { getUserInfo } from '@/services/keycloakService.js'
	import { getForloebsskabeloner } from '@/services/forløbsskabelonService.js'
	import { getOpgaveskabeloner } from '@/services/opgaveskabelonService.js'

	import CourseList from '@/components/CourseList.vue'
	import TaskList from '@/components/TaskList.vue' // Import TaskList component

	const route = useRoute()
	const router = useRouter()
	const view = route.query.view
	const _expandItem = route.query.item
	const expandItem = ref(_expandItem ? parseInt(_expandItem) : null)

	const TemplateType = {
		Forloebsskabelon: 0,
		Opgaveskabelon: 1
	}
	
	const forloebTemplates = ref([])
	const opgaveTemplates = ref([])
	const selectedType = ref(view == '0' ? TemplateType.Forloebsskabelon : view == '1' ? TemplateType.Opgaveskabelon : TemplateType.Forloebsskabelon)

	const selectTemplateType = (type) => {
		selectedType.value = type
		router.replace({ query: { view: type } })
	}

	const fetchTemplates = async () => {

		let userInfo = await getUserInfo()
		const loggedInAdmin = userInfo.email || null
		
		if(!loggedInAdmin) {
			console.error("No admin email found")
			return
		}

		const headers =  { adminmail: loggedInAdmin }
		let response

		if (selectedType.value === TemplateType.Forloebsskabelon)
			response = await getForloebsskabeloner({headers})
		else
			response = await getOpgaveskabeloner({headers})

		if (response.data == null)
			return

		if (!Array.isArray(response.data))
			response.data = [response.data]

		if (selectedType.value === TemplateType.Forloebsskabelon)
			forloebTemplates.value = response.data
		else
			opgaveTemplates.value = response.data
	}

	onMounted(fetchTemplates)
	watch(selectedType, fetchTemplates)
</script>

<template>
    <div class="flex"><div class="max-width"><!-- wrapper -->

	<div
		class="float-right helper-text"
        @mousedown.prevent
        @click.prevent
	>
		<div class="header-small">Forløbsskabeloner</div>
		<div>
			<span>Forløbsskabeloner er en skabelon til et helt forløb (med flere opgaver), som du kan genbruge til flere medarbejdere.</span>
			<span>Når du opretter et nyt forløb, kan du vælge at basere den på en forløbsskabelon. Dette vil kopiere opgaverne ind i det nye forløb – inkl. deres planlagte start- og sluttidspunkter.</span>
		</div>
		<br />
		<div class="header-small">Opgaveskabeloner</div>
		<div>
			<span>Opgaveskabeloner er en skabelon til en enkelt opgave, som kan genbruges på tværs af flere forløb og forløbsskabeloner.</span>
			<span>Når du opretter en ny opgave (i et eksisterende forløb eller på en forløbsskabelon), kan du vælge at tage udgangspunkt i en opgaveskabelon. Dette vil kopiere oplysningerne fra skabelonen til den nye opgave.</span>
		</div>
	</div>
	<div class="navItems">
		<div @click="selectTemplateType(TemplateType.Forloebsskabelon)" :class="['navItem', {'selected': selectedType==TemplateType.Forloebsskabelon}]">
			<i class="fa-regular fa-calendar fa-xl"></i>
			<span>Forløbsskabeloner</span>
		</div>
		<div @click="selectTemplateType(TemplateType.Opgaveskabelon)" :class="['navItem', {'selected': selectedType==TemplateType.Opgaveskabelon}]">
			<i class="fa-solid fa-list-ul fa-xl"></i>
			<span>Opgaveskabeloner</span>
		</div>
	</div>
    <p class="indent-tiny bold uppercase p-header-adjust">{{ selectedType==TemplateType.Forloebsskabelon ? 'Forløbsskabeloner' : 'Opgaveskabeloner' }}</p>
	<div class="buttons">
        <router-link v-if="selectedType==TemplateType.Forloebsskabelon" :to="`/create-forloebsskabelon`" class="button">+ Opret forløbsskabelon</router-link>
        <router-link v-if="selectedType==TemplateType.Opgaveskabelon" :to="`/create-opgave?template=true`" class="button">+ Opret opgaveskabelon</router-link>
    </div>
  	<CourseList v-if="selectedType==TemplateType.Forloebsskabelon" :courses="forloebTemplates" title="" />
	<TaskList v-if="selectedType==TemplateType.Opgaveskabelon"
			  :tasks="opgaveTemplates"
			  title=""
			  :expandFirstItem="false"
			  :templateView="true"
			  :expandItem="expandItem" />

	</div></div><!-- /wrapper -->
</template>

<style scoped>
.navItems {
	display: flex;
	justify-content: flex-start;
	margin-bottom: 1rem;
	gap: 0.6rem;
	border-bottom: 0.25rem solid var(--color-card-dark);
}
.navItems .navItem {
	background-color: var(--color-card-faded);
}
.navItems .navItem.selected {
	background: linear-gradient(to bottom, var(--color-card-faded), var(--color-background));
	background-color: var(--color-background);
	pointer-events: none;
	border-top: 0.25rem solid var(--color-card-dark);
	border-left: 0.25rem solid var(--color-card-dark);
	border-right: 0.25rem solid var(--color-card-dark);
	border-bottom-left-radius: 0;
	border-bottom-right-radius: 0;
	transform: translateY(0.25rem);
}
.navItems .navItem:not(.selected) {
	margin-bottom: 0.4rem;
}
</style>