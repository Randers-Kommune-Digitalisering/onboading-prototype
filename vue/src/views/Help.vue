<script setup>
import { ref, onMounted } from 'vue'

import UserInfo from '@/components/UserInfo.vue'
import { getUserInfo } from '@/services/keycloakService.js'

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
    text="Som ny medarbejder kan du se dine opgaver og følge dit aktuelle onboardingforløb.
       Du har adgang til en liste over opgaver, der skal udføres som en del af dit forløb." />
</template>