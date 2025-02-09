import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/callback',
    name: 'Callback',
    component: () => import('../views/Callback.vue')
  },
  // Other routes...
]

export default createRouter({
  history: createWebHistory(),
  routes
}) 