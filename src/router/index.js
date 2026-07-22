import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: HomePage
    },
    {
      path: '/report/:owner/:repo',
      component: () => import('../views/ReportPage.vue')
    }
  ]
})

export default router