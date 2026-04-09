import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from './pages/login.vue'
import RecommendationsPage from './pages/home.vue'
import KeywordPage from './pages/Keyword.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/recommend/:userId',
    name: 'Recommendations',
    component: RecommendationsPage,
    props: true
  },
  {
    path: '/recommend/:userId/keyword',
    name: 'Keyword',
    component: KeywordPage,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router