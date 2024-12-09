import './assets/main.css'

import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'

import App from './App.vue'

// Import af views til routing

import CreateOpgave from '@/views/CreateOpgave.vue'
import CreateForløb from '@/views/CreateForløb.vue'
import ViewOpgaver from '@/views/ViewOpgaver.vue'
import CreateRessource from '@/views/CreateRessource.vue'
import CreateForløbsskabelon from './views/CreateForløbsskabelon.vue'
import CreateOpgaveskabelon from './views/CreateOpgaveskabelon.vue'



// Opsætning af URL routing

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/create-opgave',
            name: 'CreateOpgave',
            component: CreateOpgave
        },
        {
            path: '/create-forloeb',
            name: 'CreateForloeb',
            component: CreateForløb
        },
        {
            path: '/view-opgaver',
            name: 'ViewOpgaver',
            component: ViewOpgaver
        },
        {
            path: '/create-ressource',
            name: 'CreateRessource',
            component: CreateRessource
        },
        {
            path: '/create-forloebsskabelon',
            name: 'CreateForloebsskabelon',
            component: CreateForløbsskabelon
        },
        {
            path: '/create-opgaveskabelon',
            name: 'CreateOpgaveskabelon',
            component: CreateOpgaveskabelon
        }
    ]
})

createApp(App)
.use(router)
.mount('#app')
