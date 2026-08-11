<script setup>
import {h} from 'vue'

const CalendarIcon = () => h('svg', { xmlns: '[http://www.w3.org/2000/svg](http://www.w3.org/2000/svg)', width: '22', height: '22', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('rect', { x: '3', y: '4', width: '18', height: '18', rx: '2', ry: '2' }),
  h('line', { x1: '16', y1: '2', x2: '16', y2: '6' }),
  h('line', { x1: '8', y1: '2', x2: '8', y2: '6' }),
  h('line', { x1: '3', y1: '10', x2: '21', y2: '10' })
])

const RoomIcon = () => h('svg', { xmlns: '[http://www.w3.org/2000/svg](http://www.w3.org/2000/svg)', width: '22', height: '22', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'M3 21h18' }),
  h('path', { d: 'M5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16' }),
  h('path', { d: 'M9 9h1' }),
  h('path', { d: 'M14 9h1' }),
  h('path', { d: 'M9 13h1' }),
  h('path', { d: 'M14 13h1' })
])

const DoctorIcon = () => h('svg', { xmlns: '[http://www.w3.org/2000/svg](http://www.w3.org/2000/svg)', width: '22', height: '22', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2' }),
  h('circle', { cx: '8.5', cy: '7', r: '4' }),
  h('line', { x1: '18', y1: '8', x2: '18', y2: '14' }),
  h('line', { x1: '21', y1: '11', x2: '15', y2: '11' })
])

const SyringeIcon = () => h('svg', { xmlns: '[http://www.w3.org/2000/svg](http://www.w3.org/2000/svg)', width: '22', height: '22', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'm18 2 4 4' }),
  h('path', { d: 'm17 7 3-3' }),
  h('path', { d: 'M19 9 8.7 19.3c-1 1-2.5 1-3.4 0l-.6-.6c-1-1-1-2.5 0-3.4L15 5' }),
  h('path', { d: 'm9 11 4 4' }),
  h('path', { d: 'm5 19-3 3' }),
  h('path', { d: 'm14 4 6 6' })
])
const OperationIcon = () => h('svg', { xmlns: '[http://www.w3.org/2000/svg](http://www.w3.org/2000/svg)', width: '22', height: '22', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z' })
])

const menuItems = [
  { title: 'Çizelge', path: '/schedule', icon: CalendarIcon },
  { title: 'Salonlar', path: '/rooms', icon: RoomIcon },
  { title: 'Cerrahlar', path: '/surgeons', icon: DoctorIcon },
  { title: 'Anestezi Ekipleri', path: '/anesthesia', icon: SyringeIcon },
  { title: 'Operasyonlar', path: '/operations', icon: OperationIcon }
]
</script>

<template>
<aside class="sidebar-container">
  <nav class="sidebar-nav">
    <router-link
      v-for="item in menuItems"
      :key="item.path"
      :to="item.path"
      class="nav-item"
      :title="item.title"
      >
      <div class="icon-wrapper">
        <component :is="item.icon" />
      </div>
      <span class="nav-label">{{item.title }}</span>
    </router-link>
  </nav>
</aside>

</template>

<style scoped>
.sidebar-container {
  width: 72px;
  background-color: #1e293b;
  height: calc(100vh - 60px);
  position:fixed;
  top:60px;
  left:0;
  display:flex;
  flex-direction:column;
  align-items:center;
  padding-top:20px;
  z-index:99;
  border-right:1px solid #334155;
  transition:width 0.2s ease;
}

.sidebar-nav {
  display:flex;
  flex-direction:column;
  gap:12px;
  width:100%;
  padding:0 10px;
}

.nav-item {
  display:flex;
  align-items:center;
  justify-content:center;
  height:48px;
  border-radius:10px;
  color:#94a3b8;
  text-decoration:none;
  position:relative;
  transition:all 0.2s ease;
}

.nav-item:hover{
  background-color:#334155;
  color:#ffffff;
}

.nav-item.router-link-active {
  background-color:#2563eb;
  color: #ffffff;
  box-shadow:0 4px 12px rgba(37,99,235,0.35);
}

.icon-wrapper {
  display:flex;
  align-items:center;
  justify-content:center;
}

.nav-label {
  display: none;
}

.nav-item::after {
  content:attr(title);
  position:absolute;
  left:80px;
  background:#0f172a;
  color:#fff;
  padding: 6px 12px;
  border-radius:6px;
  font-size:13px;
  white-space:nowrap;
  opacity:0;
  pointer-events:none;
  transition:opacity 0.2s ease;
  box-shadow:0 4px 6px -1px rgba(0,0,0,0.2);
}

.nav-item:hover::after{
  opacity:1;
}




</style>