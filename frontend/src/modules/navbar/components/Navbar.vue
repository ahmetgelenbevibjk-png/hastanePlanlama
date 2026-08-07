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

  <div class="nav-links">
    <router-link to="/schedule" class="nav-item">Çizelge</router-link>
      <router-link to="/rooms" class="nav-item">Salonlar</router-link>
      <router-link to="/surgeons" class="nav-item">Cerrahlar</router-link>
      <router-link to="/anesthesia" class="nav-item">Anestezi Ekipleri</router-link>
      <router-link to="/operations" class="nav-item">Operasyonlar</router-link>
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
  justify-content:space-between;
  align-items: center;
  background-color:#1e293b;
  padding:0 24px;
  height: 60px;
  color: white;
  box-shadow:0 2px 4px rgba(0,0,0,0.1);
}

.brand-title {
  font-size:1.1rem;
  font-weight:700;
  color:#f8fafc;
  text-decoration: none;
}

.nav-links {
  display :flex;
  gap: 8px;
}

.nav-item {
  color: #cbd5e1;
  text-decoration:none;
  padding:8px 16px;
  border-radius:6px;
  font-size:0.95rem;
  font-weight:500;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background-color: #334155;
  color:#ffffff;
}

.router-link-active:not(.brand-title) {
  background-color: #2563eb;
  color: #ffffff;
}

.btn-logout {
  background-color:#ef4444;
  color: white;
  border:none;
  padding:8px 16px;
  border-radius:6px;
  font-size:0.95rem;
  font-weight:500;
  cursor:pointer;
  transition:background-color 0.2s;
}

.btn-logout:hover {
  background-color: #dc2626;
}

</style>