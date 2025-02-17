<script setup>
  import { ref, onMounted } from 'vue'
  import keycloak from '@/keycloak'
  import { getForloebByEmail } from '../../services/forløbService'
  import { getOpgaverByForloebID } from '../../services/opgaveService'
  import CardList from '@/components/CardList.vue'

  const userName = ref('')
  const userFullName = ref('')
  const userRole = ref('')
  const userEmail = ref('')

  const message = ref('')

  const forloeb = ref(null)
  const forloeb_id = ref(null)
  const opgaver = ref([])


  onMounted(() => {
      if (keycloak.authenticated) {
        //console.log('User is authenticated: ', keycloak.tokenParsed)
        userName.value = keycloak.tokenParsed?.preferred_username || 'User'
        userFullName.value = keycloak.tokenParsed?.name || 'No name'
        userEmail.value = keycloak.tokenParsed?.email || 'No email'
        const clientRoles = keycloak.tokenParsed?.resource_access?.[keycloak.clientId]?.roles || []
        userRole.value = clientRoles.length > 0 ? clientRoles.join(', ') : 'No role'

        fetchOpgaver()
      }
  })

  const fetchOpgaver = async () => {
    try {
      const headers = { usermail: userEmail.value }

      if (userEmail.value) {
        
        const forloeb_response = await getForloebByEmail({ headers })
        forloeb.value = forloeb_response.data

        forloeb_id.value = forloeb.value.ForløbID
        const opgaver_response = await getOpgaverByForloebID(forloeb_id.value, { headers })
        opgaver.value = opgaver_response != null ? opgaver_response.data : null //response.data.map(opgave => ({ ...opgave, showDetails: false }))
        if (!Array.isArray(opgaver.value))
          opgaver.value = [opgaver.value]

      } else {
        console.log('Please provide user email')
      }

    } catch (error) {
      message.value = error
      opgaver.value = []
    }
  }
</script>

<template>
  {{ forloeb }}
  <CardList :taskList="opgaver" />
</template>