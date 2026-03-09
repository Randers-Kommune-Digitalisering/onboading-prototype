
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
    const accessKey = ref(null)
    const externalRequestSent = ref(false)

    const parseAccessKeyFromHash = (hash) => {
        const raw = (hash || '').toString().replace(/^#/, '')
        if (!raw)
            return null

        // Accept either `#accessKey=...` or a bare `#...` fragment.
        if (raw.startsWith('accessKey='))
            return raw.substring('accessKey='.length) || null

        const params = new URLSearchParams(raw)
        return params.get('accessKey') || raw || null
    }

    const syncAccessKey = () => {
        if (!isExternal.value)
        {
            accessKey.value = null
            return
        }

        const keyFromHash = parseAccessKeyFromHash(route.hash)
        const storageKey = id.value ? `externalAccessKey:${id.value}` : null
        const keyFromStorage = storageKey ? sessionStorage.getItem(storageKey) : null

        accessKey.value = keyFromHash || keyFromStorage || null

        // If we captured a key from the fragment, stash it and clear the fragment.
        // This reduces the chance the key is copied/screenshot from the address bar.
        if (storageKey && keyFromHash) {
            sessionStorage.setItem(storageKey, keyFromHash)
            if (route.hash)
                router.replace({ query: route.query, hash: '' })
        }
    }

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
        syncAccessKey()
        sendExternalAccessEmail()
    })
    watch(() => route.fullPath, () => {
        ensureIdOrRedirect()
        syncAccessKey()
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

        <CourseOverview v-else-if="userInfo != null && (userInfo.isAdmin || userInfo.isMedarbejder)"
                        :id="id"
                        :showDetails="true"
                        :isTemplate="isTemplate"
                        :expandItem="expandItem" />
    </div>
</template>