<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = () => {
  // Store üzerindeki logout metodunu çalıştır veya local storage'ı temizle
  if (authStore.logout) {
    authStore.logout()
  } else {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    authStore.isAuthenticated = false
  }

  // Yönlendirme yap
  router.push('/login')
}
</script>

<template>
<nav class="navbar">
  <div class="nav-brand">
    <router-link to="/schedule" class="brand-title">
      AmeliyatHane Planlama
    </router-link>
  </div>

  <div class="nav-right">
    <button @click="handleLogout" class="btn-logout">
      Çıkış Yap
    </button>
  </div>
</nav>
</template>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #312E81;
  padding: 0 24px;
  height: 60px;
  color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.brand-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #f8fafc;
  text-decoration: none;
}

.btn-logout {
  background-color: #ef4444;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-logout:hover {
  background-color: #dc2626;
}
</style>