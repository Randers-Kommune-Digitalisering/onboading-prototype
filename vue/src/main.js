import './assets/main.css'

import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'

import App from './App.vue'
import keycloak from './keycloak'

// Import af views til routing
import CreateOpgave from './views/admin/CreateOpgave.vue'
import CreateForløb from './views/admin/CreateForløb.vue'
import ViewOpgaver from '@/views/ViewOpgaver.vue'
import CreateRessource from '@/views/CreateRessource.vue'
import CreateForløbsskabelon from './views/admin/CreateForløbsskabelon.vue'
import CreateOpgaveskabelon from './views/admin/CreateOpgaveskabelon.vue'
import AdminOverview from './views/admin/AdminOverview.vue'
import AnsvarligOverview from './views/ansvarlig/AnsvarligOverview.vue'
import Start from '@/views/Start.vue'

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
        path: '/view-opgaver',
        name: 'ViewOpgaver',
        component: ViewOpgaver,
        meta: { roles: ['Admin', 'Ny medarbejder'] }
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
        meta: { roles: ['Admin'] }
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
    createApp(App)
        .use(router)
        .mount('#app')
}).catch(() => {
    console.error('Keycloak initialization failed');
});