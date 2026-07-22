import { createApp } from 'vue'
import App from './App.vue'
import { createRouter, createWebHistory } from 'vue-router'
import ReportPage from './views/ReportPage.vue'
import HomePage from './views/HomePage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: HomePage
    },
    {
      path: '/report/:owner/:repo',
      component: ReportPage
    }
  ]
})

const app = createApp(App)
app.use(router)
app.mount('#app')