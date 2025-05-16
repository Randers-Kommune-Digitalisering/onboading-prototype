<script setup>
    import { ref } from 'vue'
    import { getUserInfo } from '@/services/keycloakService.js'

    const userFullName = ref('');
    const userRoles = ref([]);

    getUserInfo().then(userInfo => {
        userFullName.value = userInfo.name || 'No name'
        userRoles.value = userInfo.roles
    }).catch(error => {
        console.error('Error fetching user info:', error);
    })
</script>

<template>
    <p class="indent-tiny bold uppercase p-header-adjust">Introduktion</p>
    <p class="indent-tiny textbox">
        Hej {{ userFullName }}!
    </p>
    <p class="indent-tiny textbox">
        Du er logget ind som en almindelig medarbejder,
        og har derfor adgang til dit eget forløb,
        samt opgaver som du er ansvarlig for at hjælpe andre med.
    </p>

    <p class="indent-tiny bold uppercase p-header-adjust-large">Mit forløb</p>
    <p class="indent-tiny textbox">
        Hvis du er ny medarbejder eller ny i din nuværende stilling, og har et igangværende onboardingforløb,
        kan du finde det under <router-link to="/medarbejder-overview">Mit forløb</router-link>.
    </p>

    <p class="indent-tiny bold uppercase p-header-adjust-large">Mine ansvar</p>
    <p class="indent-tiny textbox">
        Hvis en leder har givet dig ansvar for at hjælpe en ny medarbejder med en specifik opgave i forbindelse med deres onboardingforløb,
        kan du finde det under <router-link to="/ansvarlig-overview">Mine ansvar</router-link>.
    </p>
    <p class="indent-tiny textbox">
        Vær opmærksom på, at det er dit ansvar at markere opgaverne som færdige, efter at du har hjulpet den nye medarbejder.
        Det kan du gøre ved at klikke på opgaven og derefter klikke på knappen "Markér gennemført".
    </p>
</template>