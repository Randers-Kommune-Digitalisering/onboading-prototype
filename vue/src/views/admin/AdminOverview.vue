<script setup>
  import { ref, onMounted } from 'vue'
  import keycloak from '@/keycloak'
  import { getForloebByEmail } from '../../services/forløbService'
  import { getOpgaverByForloebID } from '../../services/opgaveService'
  import CourseList from '@/components/CourseList.vue'

  const testData = [{'id': 1, 'title': 'Demo forløb 1', 'name': 'Soren T'}]
</script>

<template>
  <CourseList :courses="testData" />
</template>