<script setup>
  import { ref, onMounted } from 'vue'

  import { getUserInfo } from '../../services/keycloakService.js'
  import CourseOverview from '@/components/CourseOverview.vue'

  const userEmail = ref('')

  getUserInfo().then(userInfo => {
    userEmail.value = userInfo.email || 'No email'
  }).catch(error => {
      console.error('Error fetching user info:', error);
  });
  
</script>

<template>
  <div v-if="userEmail != null && userEmail != ''">
    <CourseOverview :userEmail="userEmail" />
  </div>
</template>