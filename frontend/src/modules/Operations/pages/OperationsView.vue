<template>
  <div class="page-container">
    <!-- BAŞLIK VE EKLE BUTONU SEKSİYONU -->
    <div class="page-header">
      <div>
        <h2>Operasyon Yönetimi</h2>
        <p class="subtitle">Planlanacak ameliyatları, sürelerini ve sorumlu ekipleri tanımlayın.</p>
      </div>
      <button class="btn-primary-add" @click="isModalOpen = true">
        ➕ Yeni Operasyon Ekle
      </button>
    </div>

    <div class="content-grid">
      <!-- OPERASYON LİSTESİ -->
      <div class="card list-card">
        <div class="card-header space-between">
          <div class="title-with-icon">
            <div class="icon-wrapper">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>
            </div>
            <h3>Tanımlı Operasyonlar</h3>
          </div>
          <span class="count-badge">{{ operations.length }} Kayıt</span>
        </div>

        <div v-if="loading" class="state-container">
          <div class="spinner"></div>
          <p>Yükleniyor...</p>
        </div>

        <div v-else-if="error" class="state-container error">
          <p>{{ error }}</p>
        </div>

        <div v-else-if="operations.length > 0" class="table-wrapper">
          <table class="styled-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Hasta Adı</th>
                <th>Operasyon</th>
                <th>Branş</th>
                <th>Süre</th>
                <th>Öncelik</th>
                <th class="text-right">İşlemler</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="op in operations" :key="op.id">
                <td class="id-cell">#{{ op.id }}</td>
                <td><strong>{{ op.patient_name || '-' }}</strong></td>
                <td class="name-cell">
                  <span>{{ op.operation_name || op.name }}</span>
                </td>
                <td>{{ op.required_specialty || '-' }}</td>
                <td>
                  <div v-if="calculateSlots(op).slots > 0" class="duration-container">
                    <span class="duration-badge">
                      {{ calculateSlots(op).minutes }} dk
                    </span>
                    <span class="slot-badge">
                      {{ calculateSlots(op).slots }} Slot
                    </span>
                  </div>
                  <span v-else class="duration-badge empty-badge">-</span>
                </td>
                <td>
                  <span :class="['priority-badge', op.priority ? op.priority.toLowerCase() : 'normal']">
                    {{ formatPriority(op.priority) }}
                  </span>
                </td>
                <td class="text-right">
                  <button class="btn-danger-outline" @click="handleDelete(op.id)" title="Pasife Al">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    Sil
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="state-container empty">
          <div class="empty-icon">🏥</div>
          <p>Henüz kayıtlı bir operasyon bulunmuyor.</p>
        </div>
      </div>
    </div>

    <!-- Yeni Operasyon Modal Bileşeni -->
    <AddOperationModal
      :is-open="isModalOpen"
      :surgeons="surgeons"
      :anesthesia-teams="anesthesiaTeams"
      @close="isModalOpen = false"
      @created="fetchData"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { operationService } from '@/modules/Operations/services/operationService'
import { surgeonService } from '@/modules/Surgeons/services/surgeonService'
import { anesthesiaService } from '@/modules/Anesthesia/services/anesthesiaService'
import AddOperationModal from '@/modules/Operations//components/AddOperationModal.vue' 

const operations = ref([])
const surgeons = ref([])
const anesthesiaTeams = ref([])

const loading = ref(false)
const error = ref(null)
const isModalOpen = ref(false)

const fetchData = async () => {
  loading.value = true
  error.value = null

  try {
    const opRes = await operationService.getAll()
    operations.value = Array.isArray(opRes.data) ? opRes.data : (opRes.data.results || [])
  } catch (err) {
    console.error('Operasyonlar çekilirken hata:', err)
  }

  try {
    const surgRes = await surgeonService.getAll()
    surgeons.value = Array.isArray(surgRes.data) ? surgRes.data : (surgRes.data.results || [])
  } catch (err) {
    console.error('Cerrahlar çekilirken hata:', err)
  }

  try {
    const anesRes = await anesthesiaService.getAll()
    anesthesiaTeams.value = Array.isArray(anesRes.data) ? anesRes.data : (anesRes.data.results || [])
  } catch (err) {
    console.error('Anestezi ekipleri çekilirken hata:', err)
  } finally {
    loading.value = false
  }
}

const handleDelete = async (id) => {
  if (!confirm('Bu operasyonu pasife almak istediğinize emin misiniz?')) return

  try {
    await operationService.delete(id)
    await fetchData()
  } catch (err) {
    alert('Silme işlemi başarısız.')
    console.error(err)
  }
}

const formatPriority = (priority) => {
  if (!priority) return 'Normal'
  const p = priority.toString().toUpperCase()
  switch (p) {
    case 'CRITICAL':
      return 'Kritik 🚨'
    case 'HIGH':
    case 'ACIL':
      return 'Acil'
    case 'LOW':
    case 'DUSUK':
      return 'Düşük'
    case 'MEDIUM':
    case 'NORMAL':
    default:
      return 'Normal'
  }
}

const calculateSlots = (op) => {
  if (!op) return { minutes: 0, slots: 0 }

  let rawDuration =
    op.duration ??
    op.estimated_duration ??
    op.duration_minutes ??
    op.operation_duration ??
    op.time ??
    op.slots ??
    0

  if (op.slots && !op.duration) {
    const slots = parseInt(op.slots, 10) || 0
    return { minutes: slots * 30, slots }
  }

  const duration = parseInt(rawDuration, 10)

  if (!duration || isNaN(duration)) {
    return { minutes: 0, slots: 0 }
  }

  const slots = Math.ceil(duration / 30)
  return { minutes: duration, slots }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  color: #1e293b;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 6px 0;
}

.subtitle {
  color: #64748b;
  font-size: 14px;
  margin: 0;
}

.btn-primary-add {
  background: #2563eb;
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
}

.btn-primary-add:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  align-items: start;
}

.card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  padding: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f1f5f9;
}

.card-header.space-between {
  justify-content: space-between;
}

.title-with-icon {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.icon-wrapper {
  background: #eff6ff;
  color: #2563eb;
  padding: 8px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.count-badge {
  background: #f1f5f9;
  color: #475569;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
}

.btn-danger-outline {
  background: transparent;
  color: #ef4444;
  border: 1px solid #fca5a5;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.btn-danger-outline:hover {
  background: #fef2f2;
  border-color: #ef4444;
}

.table-wrapper {
  overflow-x: auto;
}

.styled-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.styled-table th {
  background: #f8fafc;
  color: #64748b;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
}

.styled-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 14px;
}

.styled-table tr:hover td {
  background: #f8fafc;
}

.id-cell {
  color: #94a3b8;
  font-weight: 600;
  font-size: 13px;
}

.name-cell {
  font-weight: 600;
  color: #0f172a;
}

.priority-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.priority-badge.critical {
  background: #7f1d1d;
  color: #ffffff;
  border: 1px solid #991b1b;
  font-weight: 700;
}

.priority-badge.high {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.priority-badge.normal {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.priority-badge.low {
  background: #f8fafc;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.text-right {
  text-align: right;
}

.state-container {
  padding: 40px 20px;
  text-align: center;
  color: #64748b;
}

.empty-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.duration-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-start;
}

.duration-badge {
  background: #f1f5f9;
  color: #334155;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.slot-badge {
  background: #e0f2fe;
  color: #0369a1;
  border: 1px solid #bae6fd;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
}

.empty-badge {
  color: #94a3b8;
}
</style>