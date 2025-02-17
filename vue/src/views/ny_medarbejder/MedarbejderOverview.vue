<script setup>
  import { ref, onMounted } from 'vue'
  import keycloak from '@/keycloak'
  import ForloebOverview from '@/components/CourseOverview.vue'

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

      console.log('User email: ', userEmail.value)

      //fetchOpgaver()
    }
  })
</script>

<template>
  <div v-if="userEmail != null && userEmail != ''">
    <ForloebOverview :userEmail="userEmail" />
  </div>
</template>