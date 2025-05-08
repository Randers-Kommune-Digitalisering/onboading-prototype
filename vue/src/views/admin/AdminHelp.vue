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
        Du er logget ind som en leder (administrator),
        og har derfor adgang til de onboardingforløb, som du er ansvarlig for,
        samt opgaver som du er ansvarlig for at hjælpe nye medarbejdere med.
    </p>

    <p class="indent-tiny bold uppercase p-header-adjust-large">Overblik</p>
    <p class="indent-tiny textbox">
        Som leder kan du se de onboardingforløb, som du er ansvarlig for, under <router-link to="/admin-overview">Overblik</router-link>.
    </p>
    <p class="indent-tiny textbox">
        Her kan du følge med i, hvordan onboardingforløbene skrider frem,
        og se hvilke opgaver der er blevet gennemført af de nye medarbejdere.
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