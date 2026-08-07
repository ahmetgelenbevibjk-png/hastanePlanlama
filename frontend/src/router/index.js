import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const routes = [
  {
    path: '/',
    redirect: '/schedule',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/modules/Auth/pages/LoginView.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/schedule',
    name: 'Schedule',
    component: () => import('@/modules/Schedule/pages/ScheduleView.vue'),
    meta: { requiresAuth: true },
  },

  // VERİ YÖNETİM SAYFALARI (NAVBAR ROTALARI)
  {
    path: '/rooms',
    name: 'Rooms',
    component: () => import('@/modules/Rooms/pages/RoomsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/surgeons',
    name: 'Surgeons',
    component: () => import('@/modules/Surgeons/pages/SurgeonsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/anesthesia',
    name: 'Anesthesia',
    component: () => import('@/modules/Anesthesia/pages/AnesthesiaView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/operations',
    name: 'Operations',
    component: () => import('@/modules/Operations/pages/OperationsView.vue'),
    meta: { requiresAuth: true },
  },

  // Tanımsız yollar için (404) Otomatik Yönlendirme
  {
    path: '/:pathMatch(.*)*',
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