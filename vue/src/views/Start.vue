<script setup>
import { ref, onMounted } from 'vue'
import keycloak from '@/keycloak'

const userName = ref('')
const userFullName = ref('')
const userRole = ref('')

onMounted(() => {
    if (keycloak.authenticated) {
        userName.value = keycloak.tokenParsed?.preferred_username || 'User'
        userFullName.value = keycloak.tokenParsed?.name || 'No name'
        const clientRoles = keycloak.tokenParsed?.resource_access?.[keycloak.clientId]?.roles || []
        userRole.value = clientRoles.length > 0 ? clientRoles.join(', ') : 'No role'
    }
})
</script>

<template>
    <h2>Velkommen til din første arbejdsdag!</h2>

    <div class="content">
        <div class="icon">
            <span>✔️</span>
        </div>
        <div class="heading">Velkommen, {{ userFullName }}!</div>
        <p>
            Fulde navn: {{ userFullName }}<br>
            Rolle: {{ userRole }}
        </p>
        <p>
            Vi er glade for at have dig med på holdet. Vi håber, du vil få en fantastisk start og ser frem til at arbejde sammen med dig.
        </p>
        <p>
            Hvis du har spørgsmål eller har brug for hjælp, er du altid velkommen til at kontakte din leder eller HR-afdelingen.
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
