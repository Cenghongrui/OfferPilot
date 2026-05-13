
import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'

const routes=[
    {
        path:'/',
        redirect:'/back/dashboard'
    },
    {
        path:'/back',
        redirect:'/back/dashboard',
        component: AppLayout,
        children:[
            {
                path:'dashboard',
                component: () => import('@/views/Dashboard.vue'),
                meta: {
                    title: '今日工作台',
                    icon: 'Menu'
                }

            },
            {
                path:'question',
                component: () => import('@/views/Questions.vue'),
                meta: {
                    title: '面试题库',
                    icon: 'Histogram'
                }
            },
            {
                path:'algorithm',
                component: () => import('@/views/Algorithms.vue'),
                meta: {
                    title: '算法练习',
                    icon: 'EditPen'
                }
            },
            {
                path:'experience',
                component: () => import('@/views/Experiences.vue'),
                meta: {
                    title: '面经笔记',
                    icon: 'Notebook'
                }
            },
            {
                path:'applications',
                component: () => import('@/views/Applications.vue'),
                meta: {
                    title: '投递看板',
                    icon: 'Message'
                }
            },
            {
                path:'mock-interview',
                component: () => import('@/views/Mock-Interview.vue'),
                meta: {
                    title: '模拟面试',
                    icon: 'Service'
                }
            },
            {
                path:'settings',
                component: () => import('@/views/Settings.vue'),
                meta: {
                    title: '设置',
                    icon: 'Setting'
                }
            },
            

        ]

    }
]


const router = createRouter({
    history:createWebHistory(),
    routes:routes
})

export default router
