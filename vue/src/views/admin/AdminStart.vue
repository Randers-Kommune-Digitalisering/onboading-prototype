<script setup>
import { ref, onMounted } from 'vue'

import UserInfo from '@/components/UserInfo.vue'
import { getUserInfo } from '../../services/keycloakService.js'

const userFullName = ref('');
const userRole = ref('');

getUserInfo().then(userInfo => {
    userFullName.value = userInfo.name || 'No name'
    userRole.value = userInfo.roles.length > 0 ? userInfo.roles.join(', ') : 'No role'
}).catch(error => {
    console.error('Error fetching user info:', error);
});
</script>

<template>
    <UserInfo :userFullName="userFullName" :userRole="userRole"
    text="Som leder kan du holde styr på dine nye medarbejdere og deres onboardingforløb. Du har adgang til en liste over igangværende og afsluttede forløb, som enten du er forfatter til, eller som er oprettet i samme forvaltning." />
</template>