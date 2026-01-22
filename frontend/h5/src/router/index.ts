import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import TraceResult from '@/pages/TraceResult.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/trace/:batchId?',
    name: 'TraceResult',
    component: TraceResult,
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/trace',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
