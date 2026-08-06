import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const routes = [
  {
    path: '/login',
    name: 'Login',
    // Dosya adınız LoginView.vue ise:
    component: () => import('@/modules/Auth/pages/LoginView.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/schedule',
    name: 'Schedule',
    // Klasörünüzdeki dosya ScheduleView.vue ise 'ScheduleView.vue' yazın:
    component: () => import('@/modules/Schedule/pages/ScheduleView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/',
    redirect: '/schedule',
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login');
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/schedule');
  } else {
    next();
  }
});

export default router;