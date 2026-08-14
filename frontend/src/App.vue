<template>
  <div id="app">

    <Sidebar v-if="showSidebar"/>

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
import Sidebar from "@modules/sidebar/pages/Sidebar.vue";

const route = useRoute()

const isAuthPage = computed(() => {
  return ['/login', '/register'].includes(route.path)
})

const showNavbar = computed(() => {
  return !['/login', '/register'].includes(route.path)
})

const showSidebar =computed(() => {
  return !isAuthPage.value
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
  margin-left:72px;
  margin-top:60px;
  min-height:calc(100vh - 60px);
  background-color: #f8fafc;
  padding:24px;
}

</style>