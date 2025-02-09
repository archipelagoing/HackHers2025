import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import LoginView from '../views/LoginView.vue';
import CallbackView from '../views/CallbackView.vue';
import MatchesView from '../views/MatchesView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/callback',
      name: 'callback',
      component: CallbackView,
      props: route => {
        const code = route.query.code;
        console.log('Callback route activated with code:', code);
        return { 
          code: code,
          state: route.query.state,
          error: route.query.error
        };
      }
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true },
      beforeEnter: (to, from, next) => {
        const token = localStorage.getItem('access_token');
        console.log('Checking auth for /home:', !!token);
        if (!token) {
          next('/login');
        } else {
          next();
        }
      }
    },
    {
      path: '/matches',
      name: 'matches',
      component: MatchesView,
      meta: { requiresAuth: true }
    }
  ]
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token');
  
  if (to.path === '/login' || to.path === '/callback') {
    next();
  } else if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');
  } else {
    next();
  }
});

export default router; 