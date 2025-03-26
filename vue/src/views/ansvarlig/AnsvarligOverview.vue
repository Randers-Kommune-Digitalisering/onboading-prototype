<script setup>
  import { ref, onMounted } from 'vue'
  import keycloak from '@/keycloak'
  import CourseOverview from '@/components/CourseOverview.vue'

  const userName = ref('')
  const userFullName = ref('')
  const userRole = ref('')
  const userEmail = ref('')

  onMounted(() => {
    if (keycloak.authenticated) {
      userName.value = keycloak.tokenParsed?.preferred_username || 'User'
      userFullName.value = keycloak.tokenParsed?.name || 'No name'
      userEmail.value = keycloak.tokenParsed?.email || null
      const clientRoles = keycloak.tokenParsed?.resource_access?.[keycloak.clientId]?.roles || []
      userRole.value = clientRoles.length > 0 ? clientRoles.join(', ') : null

      console.log('User email: ', userEmail.value)
    }
  })
</script>

<template>
  <div v-if="userEmail != null && userEmail != ''">
    <CourseOverview :ansvarligEmail="userEmail" />
  </div>
</template>