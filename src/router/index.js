
import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'

function hasSession() {
    return Boolean(localStorage.getItem('offerpilot_session'))
}

const routes=[
    {
        path:'/',
        redirect: () => hasSession() ? '/back/dashboard' : '/login'
    },
    {
        path:'/login',
        component: () => import('@/views/Login.vue'),
        meta: {
            guestOnly: true,
            title: '登录'
        }
    },
    {
        path:'/register',
        component: () => import('@/views/Register.vue'),
        meta: {
            guestOnly: true,
            title: '注册'
        }
    },
    {
        path:'/back',
        redirect:'/back/dashboard',
        component: AppLayout,
        meta: {
            requiresAuth: true
        },
        children:[
            {
                path:'dashboard',
                component: () => import('@/views/Dashboard.vue'),
                meta: {
                    title: '今日工作台',
                    icon: 'Menu',
                    group: 'main'
                }

            },
            {
                path:'question',
                component: () => import('@/views/Questions.vue'),
                meta: {
                    title: '面试题库',
                    icon: 'Histogram',
                    group: 'main'
                }
            },
            {
                path:'algorithm',
                component: () => import('@/views/Algorithms.vue'),
                meta: {
                    title: '算法练习',
                    icon: 'EditPen',
                    group: 'main'
                }
            },
            {
                path:'experience',
                component: () => import('@/views/Experiences.vue'),
                meta: {
                    title: '面经笔记',
                    icon: 'Notebook',
                    group: 'main'
                }
            },
            {
                path:'applications',
                component: () => import('@/views/Applications.vue'),
                meta: {
                    title: '投递看板',
                    icon: 'Message',
                    group: 'main'
                }
            },
            {
                path:'mock-interview',
                component: () => import('@/views/Mock-Interview.vue'),
                meta: {
                    title: '模拟面试',
                    icon: 'Service',
                    group: 'main'
                }
            },
            {
                path:'profile',
                component: () => import('@/views/Profile.vue'),
                meta: {
                    title: '个人中心',
                    icon: 'User',
                    group: 'personal'
                }
            },
            {
                path:'settings',
                component: () => import('@/views/Settings.vue'),
                meta: {
                    title: '设置',
                    icon: 'Setting',
                    group: 'personal'
                }
            },
            

        ]

    }
]


const router = createRouter({
    history:createWebHistory(),
    routes:routes
})

router.beforeEach((to) => {
    if (to.meta.requiresAuth && !hasSession()) {
        return '/login'
    }

    if (to.meta.guestOnly && hasSession()) {
        return '/back/dashboard'
    }

    return true
})

export default router
