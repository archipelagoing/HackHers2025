import { createRouter, createWebHistory } from 'vue-router';

export function createTestRouter() {
  return createRouter({
    history: createWebHistory(),
    routes: [
      {
        path: '/',
        name: 'home',
        component: () => import('../../views/HomeView.vue')
      },
      // Add other routes as needed
    ]
  });
} 