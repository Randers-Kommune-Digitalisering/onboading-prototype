<script setup>
import { ref, onMounted } from 'vue'
import keycloak from '@/keycloak'
import UserInfo from '@/components/UserInfo.vue'

const userName = ref('')
const userFullName = ref('')
const userRole = ref('')
const userEmail = ref('')

onMounted(() => {
    if (keycloak.authenticated) {
        userName.value = keycloak.tokenParsed?.preferred_username || 'User'
        userFullName.value = keycloak.tokenParsed?.name || 'No name'
        userEmail.value = keycloak.tokenParsed?.email || 'No email'
        const clientRoles = keycloak.tokenParsed?.resource_access?.[keycloak.clientId]?.roles || []
        userRole.value = clientRoles.length > 0 ? clientRoles.join(', ') : 'No role'
    }
})
</script>

<template>
    <UserInfo :userFullName="userFullName" :userRole="userRole"
    text="Som ansvarlig kan du holde styr på dine nye kollegaer samt opgaversom du er ansvarlig for." />
</template>