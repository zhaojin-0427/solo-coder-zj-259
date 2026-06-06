import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/cellar-pools' },
  { path: '/cellar-pools', component: () => import('@/views/CellarPools.vue'), name: '窖池管理' },
  { path: '/fermentation', component: () => import('@/views/Fermentation.vue'), name: '发酵监控' },
  { path: '/wine-quality', component: () => import('@/views/WineQuality.vue'), name: '酒质登记' },
  { path: '/aging-storage', component: () => import('@/views/AgingStorage.vue'), name: '陈酿库位' },
  { path: '/statistics', component: () => import('@/views/Statistics.vue'), name: '统计分析' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
