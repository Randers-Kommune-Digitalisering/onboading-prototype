
<script setup>
    import { useRoute, useRouter } from 'vue-router'
    import CourseOverview from '@/components/CourseOverview.vue'
    import { getUserInfo } from '@/services/keycloakService.js'
    import { onMounted, ref, computed, watch } from 'vue'
    import { requestExternalAccess } from '@/services/externalAccessService.js'

    const route = useRoute()
    const router = useRouter()
    const id = computed(() => parseInt(route.query.id || route.query.tid, 10))
    const isTemplate = computed(() => route.query.tid !== undefined)
	const _expandItem = route.query.item
	const expandItem = ref(_expandItem ? parseInt(_expandItem) : null)
    const userInfo = ref(null)

    const isExternal = computed(() => (route.query.external || '').toString().toLowerCase() === 'true')
    const accessKey = computed(() => (route.query.accessKey || '').toString() || null)
    const externalRequestSent = ref(false)

    const ensureIdOrRedirect = () => {
        if (!id.value || Number.isNaN(id.value))
            router.replace({ path: '/' })
    }

    getUserInfo().then((response) => {
        userInfo.value = response
    }).catch((error) => {
        console.error('Error fetching user info:', error)
    })

    const sendExternalAccessEmail = async () => {
        if (!isExternal.value)
            return
        if (!id.value || Number.isNaN(id.value))
            return
        if (accessKey.value)
            return
        if (externalRequestSent.value)
            return

        externalRequestSent.value = true
        try {
            await requestExternalAccess(id.value)
        } catch (error) {
            console.error('Error requesting external access:', error)
        }
    }

    onMounted(() => {
        ensureIdOrRedirect()
        sendExternalAccessEmail()
    })
    watch(() => route.query, () => {
        ensureIdOrRedirect()
        sendExternalAccessEmail()
    })
    
</script>

<template>
    <div>
        <div v-if="isExternal">
            <p v-if="!accessKey" class="indent-tiny notification">
                <span class="bold">OBS</span>: Tjek din email for et link til at åbne forløbet.
            </p>
            <CourseOverview v-else
                            :id="id"
                            :showDetails="true"
                            :isTemplate="false"
                            :expandItem="expandItem"
                            :external="true"
                            :accessKey="accessKey" />
        </div>

        <CourseOverview v-else-if="userInfo != null && (userInfo.isAdmin || userInfo.isAnsvarlig)"
                        :id="id"
                        :showDetails="true"
                        :isTemplate="isTemplate"
                        :expandItem="expandItem" />
    </div>
</template>