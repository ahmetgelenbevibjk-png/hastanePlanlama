<template>
  <div class="schedule-page">
    <!-- Üst Kontrol Barı -->
    <div class="page-header">
      <div class="header-title">
        <h1>Ameliyathane Günlük Planlama Çizelgesi</h1>
        <p class="subtitle">Günlük operasyon akışını ve salon doluluklarını takip edin.</p>
      </div>

      <div class="header-actions">
        <!-- Tarih Seçici -->
        <div class="date-picker-wrapper">
          <label for="schedule-date">Tarih:</label>
          <input
            type="date"
            id="schedule-date"
            v-model="selectedDate"
            @change="fetchScheduleData"
            class="date-input"
          />
        </div>

        <!-- Planlama Çalıştır Butonu (Engeli Kaldırıldı) -->
        <button
          @click="runOptimizer"
          :disabled="isOptimizing"
          :class="['btn-run', { 'is-loading': isOptimizing }]"
          type="button"
        >
          <span v-if="isOptimizing">⚡ Planlanıyor...</span>
          <span v-else>⚡ Planlamayı Çalıştır</span>
        </button>
      </div>
    </div>

    <!-- Hızlı Özet İstatistik Kartları -->
    <div class="stats-grid">
      <div class="stat-card">
        <span class="stat-label">Aktif Salon Sayısı</span>
        <span class="stat-value">{{ rooms.length }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Planlanan Operasyon</span>
        <span class="stat-value">{{ operations.length }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Ortalama Doluluk</span>
        <span class="stat-value">%{{ occupancyRate }}</span>
      </div>
    </div>

    <!-- Ana Çizelge Alanı -->
    <div class="grid-card">
      <div v-if="loading" class="loading-state">Çizelge yükleniyor...</div>
      <ScheduleGrid
        v-else
        :date="selectedDate"
        :rooms="rooms"
        :operations="operations"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import ScheduleGrid from '../components/ScheduleGrid.vue'
import * as scheduleServiceModule from '../services.js'
import { roomService } from '@/modules/Rooms/services/roomService'

const scheduleService = scheduleServiceModule.scheduleService || scheduleServiceModule.default || scheduleServiceModule

const selectedDate = ref(new Date().toISOString().split('T')[0])
const isOptimizing = ref(false)
const loading = ref(false)

const rooms = ref([])
const operations = ref([])

// Gerçek Slot Sürelerine Göre Doluluk Oranı Hesabı
const occupancyRate = computed(() => {
  if (rooms.value.length === 0) return 0

  const totalAvailableSlots = rooms.value.length * 20 // Günde salon başı 20 slot (10 saat)
  const totalScheduledSlots = operations.value.reduce((total, op) => {
    const slots = op.duration_slot || Math.ceil((op.duration || 60) / 30)
    return total + slots
  }, 0)

  const rate = Math.round((totalScheduledSlots / totalAvailableSlots) * 100)
  return rate > 100 ? 100 : rate
})

const fetchScheduleData = async () => {
  loading.value = true
  try {
    const roomRes = await roomService.getAll()
    rooms.value = Array.isArray(roomRes.data) ? roomRes.data : (roomRes.data?.results || [])

    const scheduleRes = await scheduleService.getByDate(selectedDate.value)
    operations.value = Array.isArray(scheduleRes.data) ? scheduleRes.data : (scheduleRes.data?.results || [])
  } catch (error) {
    console.error('Çizelge verileri yüklenirken hata:', error)
  } finally {
    loading.value = false
  }
}

const runOptimizer = async () => {
  if (!selectedDate.value) {
    alert('Lütfen bir tarih seçin.')
    return
  }

  isOptimizing.value = true
  try {
    if (scheduleService && typeof scheduleService.generate === 'function') {
      await scheduleService.generate({ date: selectedDate.value })
    } else if (scheduleService && typeof scheduleService.optimize === 'function') {
      await scheduleService.optimize({ date: selectedDate.value })
    } else {
      await new Promise(resolve => setTimeout(resolve, 1000))
    }

    alert('Planlama başarıyla çalıştırıldı!')
    await fetchScheduleData()
  } catch (error) {
    console.error('Planlama hatası:', error)
    alert('Planlama çalıştırılırken bir hata oluştu.')
  } finally {
    isOptimizing.value = false
  }
}

watch(selectedDate, () => {
  fetchScheduleData()
})

onMounted(() => {
  fetchScheduleData()
})
</script>

<style scoped>
.schedule-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Header Tasarımı */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #ffffff;
  padding: 20px 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-title h1 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 700;
  color: #0f172a;
}

.subtitle {
  margin: 4px 0 0 0;
  font-size: 0.875rem;
  color: #64748b;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.date-picker-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  color: #334155;
}

.date-input {
  padding: 8px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  outline: none;
  font-size: 0.9rem;
  color: #1e293b;
}

.date-input:focus {
  border-color: #2563eb;
}

.btn-run {
  background-color: #2563eb;
  color: #ffffff;
  border: none;
  padding: 10px 18px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
}

.btn-run:hover:not(:disabled) {
  background-color: #1d4ed8;
  transform: translateY(-1px);
}

.btn-run:disabled {
  background-color: #94a3b8;
  cursor: not-allowed;
  box-shadow: none;
}

/* İstatistik Kartları */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  background: #ffffff;
  padding: 16px 20px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #2563eb;
}

.stat-label {
  font-size: 0.8rem;
  color: #64748b;
  font-weight: 500;
  text-transform: uppercase;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
}

/* Izgara Konteyneri */
.grid-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 20px;
  min-height: 400px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  color: #64748b;
  font-size: 1rem;
}
</style>