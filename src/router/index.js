import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import AuthCallback from '../views/AuthCallback.vue'
import Editor from '../views/Editor.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/editor',
    name: 'Editor',
    component: Editor,
    meta: { requiresAuth: true }
  },
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: AuthCallback
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Route guards
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token')
    if (!token) {
      next('/')
      return
    }
  }
  next()
})

export default router