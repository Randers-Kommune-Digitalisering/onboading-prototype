import './assets/main.css'

import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'

import App from './App.vue'
import keycloak from './keycloak.js'

// Import af views til routing
import CreateOpgave from '@/views/admin/CreateOpgave.vue'
import CreateForløb from '@/views/admin/CreateForløb.vue'
import CreateRessource from '@/views/admin/CreateRessource.vue'
import CreateForløbsskabelon from '@/views/admin/CreateForløbsskabelon.vue'
import AdminOverview from '@/views/admin/AdminOverview.vue'
import AnsvarligOverview from '@/views/ansvarlig/AnsvarligOverview.vue'
import AnsvarligStart from '@/views/ansvarlig/AnsvarligStart.vue'
import AdminStart from '@/views/admin/AdminStart.vue'
import MedarbejderStart from '@/views/ny_medarbejder/MedarbejderStart.vue'
import MedarbejderOverview from '@/views/ny_medarbejder/MedarbejderOverview.vue'
import ForløbOverview from '@/views/ForløbOverview.vue'
import TemplateOverview from '@/views/admin/TemplateOverview.vue'
import Blank from '@/views/Blank.vue'

// Define routes
const routes = [ 
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
        path: '/template-overview',
        name: 'TemplateOverview',
        component: TemplateOverview,
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
    },
    
    {
        path: '/forloeb-overview',
        name: 'ForløbOverview',
        component: ForløbOverview,
        meta: { roles: ['Admin', 'Ansvarlig'] }
    },
    {
        path: '/reload',
        name: 'Reload',
        component: Blank,
        meta: { roles: ['Admin', 'Ansvarlig', 'Ny medarbejder'] }
    }
]

// Opsætning af URL routing
const router = createRouter({
    history: createWebHistory(),
    routes
})

// Initialize Keycloak and then create the Vue app
keycloak.init({ onLoad: 'login-required' }).then(() => {
    const app = createApp(App)
    app.use(router)

    // Check roles and redirect if necessary
    const userRoles = keycloak.tokenParsed?.resource_access?.[keycloak.clientId]?.roles || []

    const currentPath = window.location.pathname
    const currentRoute = window.location.pathname + window.location.search
    router.addRoute({ path: currentRoute })

    // TODO: Only push to overview if user is not on other accepted page
    if (userRoles.includes('Admin') && currentPath === '/') {
        router.push('/admin-overview')
    } else if (userRoles.includes('Ansvarlig') && currentPath === '/') {
        router.push('/ansvarlig-overview')
    } else if (userRoles.includes('Ny medarbejder') && currentPath === '/') {
        router.push('/medarbejder-overview')
    }

    app.mount('#app')
}).catch(() => {
    console.error('Keycloak initialization failed');
});