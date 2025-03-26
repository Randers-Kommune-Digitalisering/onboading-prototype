<script>
  import keycloak from '../keycloak';

  export default {
    methods: {
      login() {
        keycloak.login();
      }
    }
  }
</script>
<template></template>