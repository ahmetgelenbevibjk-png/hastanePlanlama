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
            class="date-input"
          />
        </div>

        <!-- Alternatif Planlar Modalı Açma Butonu -->
        <button
          v-if="candidatePlans.length > 0"
          @click="isCandidatesModalOpen = true"
          class="btn-results"
          type="button"
        >
          📊 Alternatif Planlar ({{ candidatePlans.length }})
        </button>

        <!-- Planlama Çalıştır Butonu -->
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
        <span class="stat-value">{{ scheduledOperations.length }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Ortalama Doluluk</span>
        <span class="stat-value">%{{ occupancyRate }}</span>
      </div>
      <!-- Plan Uygunluk Skoru (Fitness Score) Kartı -->
      <div v-if="fitnessScore !== null" class="stat-card fitness-card">
        <span class="stat-label">Plan Uygunluk Skoru</span>
        <span :class="['stat-value', fitnessColorClass]">%{{ fitnessScore }}</span>
      </div>
    </div>

    <!-- Ana Çizelge Alanı -->
    <div class="grid-card">
      <div v-if="loading" class="loading-state">Çizelge yükleniyor...</div>
      <ScheduleGrid
        v-else
        :date="selectedDate"
        :rooms="rooms"
        :operations="scheduledOperations"
        :surgeons="surgeons"
        :anesthesia-teams="anesthesiaTeams"
        @select-operation="handleSelectOperation"
      />
    </div>

    <!-- Aday Planlar Modalı Component -->
    <CandidatesModal
      :is-open="isCandidatesModalOpen"
      :candidates="candidatePlans"
      :selected-candidate-id="selectedPlanId"
      @close="isCandidatesModalOpen = false"
      @select-plan="handleSelectPlan"
    />

    <!-- Ameliyat Detay Modalı Component -->
    <OperationDetailModal
      :is-open="isDetailModalOpen"
      :operation="selectedOp"
      :rooms="rooms"
      :surgeons="surgeons"
      :anesthesia-teams="anesthesiaTeams"
      @close="closeDetailModal"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import ScheduleGrid from '../components/ScheduleGrid.vue'
import CandidatesModal from '../components/CandidatesModal.vue'
import OperationDetailModal from '../pages/OperationDetailModal.vue'
import { ScheduleService } from '../services.js'

const getTodayString = () => {
  const d = new Date()
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const selectedDate = ref(getTodayString())
const isOptimizing = ref(false)
const loading = ref(false)

const rooms = ref([])
const operations = ref([])
const scheduledOperations = ref([])
const surgeons = ref([])
const anesthesiaTeams = ref([])

// Başlangıç Skor ve Aday Plan Test Verileri
const fitnessScore = ref(63.6)
const selectedPlanId = ref(1)

const candidatePlans = ref([
  {
    candidate_id: 1,
    strategy_name: "Öncelik Odaklı Senaryo",
    fitness_score: 63.6,
    assigned_count: 7,
    unassigned_count: 0,
    total_penalty: 36.4,
    penalties: [
      { reason: "HIGH Öncelikli Vaka (P1) Geciktirildi", points: 15 },
      { reason: "08:00 - 09:30 OR-1 Salon Atıl Süresi", points: 11.4 },
      { reason: "Team-B Ekibinin Dinlenmesiz Ameliyat Dizilimi", points: 10 }
    ]
  },
  {
    candidate_id: 2,
    strategy_name: "Erken Başlangıç Senaryosu",
    fitness_score: 79.0,
    assigned_count: 7,
    unassigned_count: 0,
    total_penalty: 21.0,
    penalties: [
      { reason: "08:00 Slotunda OR-4 Salonu Atıl Kaldı", points: 11.0 },
      { reason: "Ekip Turnaround Süre Aşımı", points: 10.0 }
    ]
  }
])

// Modal Durum Kontrolleri
const isCandidatesModalOpen = ref(false)
const isDetailModalOpen = ref(false)
const selectedOp = ref(null)

const handleSelectOperation = (op) => {
  selectedOp.value = op
  isDetailModalOpen.value = true
}

const closeDetailModal = () => {
  isDetailModalOpen.value = false
  selectedOp.value = null
}

// Alternatif Plan Seçildiğinde Çizelgeyi Günceller
const handleSelectPlan = (plan) => {
  selectedPlanId.value = plan.candidate_id || plan.id
  fitnessScore.value = plan.fitness_score
  if (plan.assigned && plan.assigned.length > 0) {
    scheduledOperations.value = plan.assigned
  }
}

const fitnessColorClass = computed(() => {
  if (fitnessScore.value === null) return ''
  if (fitnessScore.value >= 80) return 'text-success'
  if (fitnessScore.value >= 50) return 'text-warning'
  return 'text-danger'
})

const occupancyRate = computed(() => {
  if (rooms.value.length === 0) return 0
  const totalAvailableSlots = rooms.value.length * 20
  const totalScheduledSlots = scheduledOperations.value.reduce((total, op) => {
    const slots = op.duration_slot || Math.ceil((op.duration || 60) / 30)
    return total + slots
  }, 0)

  const rate = Math.round((totalScheduledSlots / totalAvailableSlots) * 100)
  return rate > 100 ? 100 : rate
})

const fetchScheduleData = async () => {
  loading.value = true
  try {
    const roomRes = await ScheduleService.getRooms()
    rooms.value = Array.isArray(roomRes.data) ? roomRes.data : (roomRes.data?.results || [])

    const opRes = await ScheduleService.getOperations()
    const allOps = Array.isArray(opRes.data) ? opRes.data : (opRes.data?.results || [])
    operations.value = allOps

    scheduledOperations.value = allOps.filter(op =>
      (op.room_id || op.room) && (op.start_slot !== null && op.start_slot !== undefined)
    )

    if (ScheduleService.getSurgeons) {
      const surgeonRes = await ScheduleService.getSurgeons()
      surgeons.value = Array.isArray(surgeonRes.data) ? surgeonRes.data : (surgeonRes.data?.results || [])
    }
    if (ScheduleService.getAnesthesiaTeams) {
      const anesthesiaRes = await ScheduleService.getAnesthesiaTeams()
      anesthesiaTeams.value = Array.isArray(anesthesiaRes.data) ? anesthesiaRes.data : (anesthesiaRes.data?.results || [])
    }
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
    const [year, month, day] = selectedDate.value.split('-').map(Number)
    const dateObj = new Date(year, month - 1, day)
    const dayName = dateObj.toLocaleDateString('tr-TR', { weekday: 'long' })

    const response = await ScheduleService.runScheduler({
      date: selectedDate.value,
      day_name: dayName
    })

    const resData = response.data
    if (resData) {
      if (resData.best_plan) {
        fitnessScore.value = resData.best_plan.fitness_score
        scheduledOperations.value = resData.best_plan.assigned || []
        selectedPlanId.value = resData.best_plan.candidate_id
      } else if (resData.fitness_score !== undefined) {
        fitnessScore.value = resData.fitness_score
        scheduledOperations.value = resData.assigned || []
      }

      const candidatesList = resData.all_candidates || resData.candidates
      if (candidatesList && candidatesList.length > 0) {
        candidatePlans.value = candidatesList
      }

      const assignedCount = resData.best_plan?.assigned_count || scheduledOperations.value.length
      const unassignedCount = resData.best_plan?.unassigned_count || 0

      alert(`Optimizasyon tamamlandı!\n- Üretilen Alternatif Senaryo: ${candidatePlans.value.length}\n- Atanan Operasyon: ${assignedCount}\n- Atanamayan Operasyon: ${unassignedCount}`)
    }
  } catch (error) {
    console.error('Planlama hatası:', error)
    const errMessage = error.response?.data?.message || error.response?.data?.error || 'Planlama çalıştırılırken bir hata oluştu.'
    alert(errMessage)
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

.btn-results {
  background-color: #4f46e5;
  color: #ffffff;
  border: none;
  padding: 10px 18px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2);
}
.btn-results:hover {
  background-color: #4338ca;
  transform: translateY(-1px);
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

.fitness-card {
  border-left-color: #059669 !important;
}
.text-success {
  color: #059669;
}
.text-warning {
  color: #d97706;
}
.text-danger {
  color: #dc2626;
}

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