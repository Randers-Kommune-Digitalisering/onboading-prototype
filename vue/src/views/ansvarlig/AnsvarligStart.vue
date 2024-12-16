<script setup>
import { ref, onMounted } from 'vue'
import keycloak from '@/keycloak'

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
    <h2>Ansvarlig Introduktion</h2>

    <div class="content">
        <div class="icon">
            <span>✔️</span>
        </div>
        <div class="heading">Velkommen, {{ userFullName }}!</div>
        <p>
            Fulde navn: {{ userFullName }}<br>
            Rolle: {{ userRole }}<br>
            Email: {{ userEmail }}
        </p>
        <p>
            Som ansvarlig kan du holde styr på dine nye medarbejdere og opgaver hvor du er sat som ansvarlig kan ses.
        </p>
    </div>
</template>

<style scoped>
.content {
    border: 1px solid #ccc;
    padding: 16px;
    margin-bottom: 16px;
}
.icon {
    font-size: 24px;
    margin-bottom: 8px;
}
.heading {
    font-weight: bold;
    margin-bottom: 8px;
}
</style>