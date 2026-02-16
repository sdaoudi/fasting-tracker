import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: () => import('../views/Dashboard.vue') },
    { path: '/start', name: 'start', component: () => import('../views/StartFast.vue') },
    { path: '/fast/:id', name: 'fast-detail', component: () => import('../views/FastDetail.vue') },
    { path: '/history', name: 'history', component: () => import('../views/History.vue') },
    { path: '/stats', name: 'stats', component: () => import('../views/StatsView.vue') },
    { path: '/weight', name: 'weight', component: () => import('../views/WeightView.vue') },
    { path: '/meals', name: 'meals', component: () => import('../views/MealsView.vue') },
  ],
})

export default router
