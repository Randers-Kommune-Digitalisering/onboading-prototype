import './assets/main.css'

import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'

import App from './App.vue'
import keycloak from './keycloak'

// Import af views til routing
import CreateOpgave from './views/admin/CreateOpgave.vue'
import CreateForløb from './views/admin/CreateForløb.vue'
import CreateRessource from '@/views/CreateRessource.vue'
import CreateForløbsskabelon from './views/admin/CreateForløbsskabelon.vue'
import CreateOpgaveskabelon from './views/admin/CreateOpgaveskabelon.vue'
import AdminOverview from './views/admin/AdminOverview.vue'
import AnsvarligOverview from './views/ansvarlig/AnsvarligOverview.vue'
import AnsvarligStart from './views/ansvarlig/AnsvarligStart.vue'
import AdminStart from './views/admin/AdminStart.vue'
import Start from '@/views/Start.vue'
import MedarbejderStart from './views/ny_medarbejder/MedarbejderStart.vue'
import MedarbejderOverview from './views/ny_medarbejder/MedarbejderOverview.vue'

// Define routes
const routes = [
    {
        path: '/', 
        name: "Start",
        component: Start
    },   
    {
        path: '/create-opgave',
        name: 'CreateOpgave',
        component: CreateOpgave,
        meta: { roles: ['Admin'] }
    },
    {
        path: '/create-forloeb',
        name: 'CreateForløb',
        component: CreateForløb,
        meta: { roles: ['Admin'] }
    },
    {
        path: '/create-ressource',
        name: 'CreateRessource',
        component: CreateRessource,
        meta: { roles: ['Admin'] }
    },
    {
        path: '/create-forloebsskabelon',
        name: 'CreateForløbsskabelon',
        component: CreateForløbsskabelon,
        meta: { roles: ['Admin'] }
    },
    {
        path: '/create-opgaveskabelon',
        name: 'CreateOpgaveskabelon',
        component: CreateOpgaveskabelon,
        meta: { roles: ['Admin'] }
    },
    {
        path: '/admin-overview',
        name: 'AdminOverview',
        component: AdminOverview,
        meta: { roles: ['Admin'] }
    },
    {
        path: '/ansvarlig-overview',
        name: 'AnsvarligOverview',
        component: AnsvarligOverview,
        meta: { roles: ['Ansvarlig'] }
    },
    {
        path: '/admin-start',
        name: 'AdminStart',
        component: AdminStart,
        meta: { roles: ['Admin'] }
    },
    
    {
        path: '/ansvarlig-start',
        name: 'AnsvarligStart',
        component: AnsvarligStart,
        meta: { roles: ['Ansvarlig'] }
    },
    {
        path: '/medarbejder-start',
        name: 'MedarbejderStart',
        component: MedarbejderStart,
        meta: { roles: ['Ny medarbejder'] }
    },
    {
        path: '/medarbejder-overview',
        name: 'MedarbejderOverview',
        component: MedarbejderOverview,
        meta: { roles: ['Ny medarbejder'] }
    }
]

// Opsætning af URL routing
const router = createRouter({
    history: createWebHistory(),
    routes
})

// Navigation guard to check roles
router.beforeEach((to, from, next) => {
    if (keycloak.authenticated) {
        const userRoles = keycloak.tokenParsed?.resource_access?.[keycloak.clientId]?.roles || []
        if (to.meta.roles) {
            const hasAccess = to.meta.roles.some(role => userRoles.includes(role))
            if (hasAccess) {
                next()
            } else {
                next('/') // Redirect to Start page if no access
            }
        } else {
            next() // No roles required, allow access
        }
    } else {
        next('/') // Redirect to Start page if not authenticated
    }
})

// Initialize Keycloak and then create the Vue app
keycloak.init({ onLoad: 'login-required' }).then(() => {
    const app = createApp(App)
    app.use(router)

    // Check roles and redirect if necessary
    const userRoles = keycloak.tokenParsed?.resource_access?.[keycloak.clientId]?.roles || []
    if (userRoles.includes('Admin')) {
        router.push('/admin-start')
    } else if (userRoles.includes('Ansvarlig')) {
        router.push('/ansvarlig-start')
    } else if (userRoles.includes('Ny medarbejder')) {
        router.push('/medarbejder-start')
    }

    app.mount('#app')
}).catch(() => {
    console.error('Keycloak initialization failed');
});