import './assets/main.css'

import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'

import App from './App.vue'

import { getUserInfo } from './services/keycloakService.js'

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
import DownloadForløb from './views/DownloadForløb.vue'

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
        path: '/forloeb-download',
        name: 'DownloadForloeb',
        component: DownloadForløb,
        meta: { roles: ['Admin', 'Ansvarlig'], hideNavbar: true }
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

const app = createApp(App)
app.use(router)

const currentPath = window.location.pathname
const currentRoute = window.location.pathname + window.location.search
router.addRoute({ path: currentRoute })

router.beforeEach((to, from, next) => {
    getUserInfo().then(userInfo => {
        let userRoles = userInfo.roles

        if (to.matched.some(record => record.meta.roles)) {
            const requiredRoles = to.meta.roles
            const hasAccess = requiredRoles.some(role => userRoles.includes(role))

            if (!hasAccess) {
                // User does not have access to requested route
                returnRoleBasedUrl(userInfo).then(url => {
                    next(url)
                })
                
            } else {
                next()
            }
        } else {
            returnRoleBasedUrl(userInfo).then(url => {
                next(url)
            })
        }
    }).catch(() => {
        next({ path: '/login' })
    })
})

const returnRoleBasedUrl = async (_userInfo = null) => {
    try {
        const userInfo = _userInfo ?? await getUserInfo()
        let userRoles = userInfo.roles

        if (userRoles.includes('Admin'))
            return '/admin-overview'
        else if (userRoles.includes('Ansvarlig'))
            return '/ansvarlig-overview'
        else if (userRoles.includes('Ny medarbejder'))
            return '/medarbejder-overview'
        else
            return '/login'
        
    } catch {
        return '/login'
    }
}

if (currentPath === '/')
    returnRoleBasedUrl().then(url => {
        router.push(url)
    })

app.mount('#app')