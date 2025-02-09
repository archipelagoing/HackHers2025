import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import MatchesView from '../views/MatchesView.vue'
import PlaylistsView from '@/views/PlaylistsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/home',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/matches',
      name: 'matches',
      component: MatchesView
    },
    {
      path: '/playlists',
      name: 'playlists',
      component: PlaylistsView
    }
  ],
})

export default router
