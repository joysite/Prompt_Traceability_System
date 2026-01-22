import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import BatchList from '@/pages/BatchList.vue'
import Login from '@/pages/Login.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
  {
    path: '/',
    redirect: '/batches',
  },
  {
    path: '/batches',
    name: 'BatchList',
    component: BatchList,
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('admin_token')
  if (to.meta.requiresAuth && !token) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else if (to.path === '/login' && token) {
    next('/batches')
  } else {
    next()
  }
})

export default router
