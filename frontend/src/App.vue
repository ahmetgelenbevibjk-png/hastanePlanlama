<template>
  <div id="app">

    <Navbar v-if="showNavbar" />

    <main class="main-content">
          <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './modules/navbar/components/Navbar.vue'

const route = useRoute()

const showNavbar = computed(() => {
  return !['/login', '/register'].includes(route.path)
})
</script>

<style>
body {
  margin:0;
  padding: 0;
  font-family: system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto, sans-serif;
  background-color: #f8fafc;
}

.main-content {
  padding:24px;
}

</style>