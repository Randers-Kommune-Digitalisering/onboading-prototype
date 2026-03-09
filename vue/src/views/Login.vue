<script setup>
    import { onMounted, ref } from 'vue'
    import { useRouter } from 'vue-router'
    import { getUserInfo } from '@/services/keycloakService.js'

    const router = useRouter()
    const userInfo = ref({
        roles: [],
        email: '',
        isAdmin: false,
        isAnsvarlig: false,
        isMedarbejder: false,
    })

    onMounted(async () => {
        try {
            userInfo.value = await getUserInfo()
            if (userInfo.value?.email) {
                const latestRoute = router.options.history.state.back || '/';
                router.replace(latestRoute);
            }
        } catch (error) {
            console.error(error)
        }
    })
</script>

<template>
    <div class="login-container">
        <p>Du er ikke logget ind</p>
        <a href="/login">Log ind med KOMBIT</a>
    </div>
</template>

<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    height: 100vh;
    background-color: var(--background-color);
}
p {
    color: var(--text-color);
    font-size: 1.2em;
    font-weight: 500;
    margin: 0;
    padding-bottom: 1rem;
    padding-top: 1rem;
    text-align: center;
}
a {
    color: rgb(84, 86, 164);
}
</style>