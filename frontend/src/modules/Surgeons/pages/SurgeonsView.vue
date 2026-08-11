<script setup>
import { ref, onMounted } from 'vue'
import { surgeonService } from '../services/surgeonService'

const surgeons = ref([])
const loading = ref(false)
const submitting = ref(false)
const error = ref(null)

const newSurgeon = ref({
  name: '',
  specialty: '',
  off_day: ''
})

const daysOfWeek = [
  { value: 'monday', label: 'Pazartesi' },
  { value: 'tuesday', label: 'Salı' },
  { value: 'wednesday', label: 'Çarşamba' },
  { value: 'thursday', label: 'Perşembe' },
  { value: 'friday', label: 'Cuma' },
  { value: 'saturday', label: 'Cumartesi' },
  { value: 'sunday', label: 'Pazar' }
]

const fetchSurgeons = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await surgeonService.getAll()
    surgeons.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
  } catch (err) {
    error.value = 'Cerrah listesi yüklenirken hata oluştu.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  if (!newSurgeon.value.name.trim()) return

  submitting.value = true
  try {
    await surgeonService.create(newSurgeon.value)
    newSurgeon.value = { name: '', specialty: '', off_day: '' }
    await fetchSurgeons()
  } catch (err) {
    alert('Cerrah eklenirken hata oluştu!')
    console.error(err)
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id) => {
  if (!confirm('Bu doktoru pasife almak istediğinize emin misiniz?')) return

  try {
    await surgeonService.delete(id)
    await fetchSurgeons()
  } catch (err) {
    alert('Silme işlemi başarısız.')
    console.error(err)
  }
}

const formatDay = (dayKey) => {
  if (!dayKey) return 'İzin Yok'
  const found = daysOfWeek.find(d => d.value.toLowerCase() === dayKey.toLowerCase())
  return found ? found.label : dayKey
}

onMounted(() => {
  fetchSurgeons()
})
</script>

<template>
  <div class="page-container">
    <!-- BAŞLIK SEKSİYONU -->
    <div class="page-header">
      <div>
        <h2>Cerrah Yönetimi</h2>
        <p class="subtitle">Sistemdeki uzman doktorları ve branşlarını yönetin.</p>
      </div>
    </div>

    <div class="content-grid">
      <!-- SOL: YENİ CERRAH EKLEME FORMU -->
      <div class="card form-card">
        <div class="card-header">
          <div class="icon-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line></svg>
          </div>
          <h3>Yeni Cerrah Ekle</h3>
        </div>

        <form @submit.prevent="handleCreate" class="styled-form">
          <div class="form-group">
            <label for="surgeonName">Doktor Adı Soyadı</label>
            <input
              id="surgeonName"
              v-model="newSurgeon.name"
              type="text"
              placeholder="Örn: Prof. Dr. Ahmet Yılmaz"
              required
            />
          </div>

          <div class="form-group">
            <label for="specialty">Uzmanlık Alanı / Branş</label>
            <input
              id="specialty"
              v-model="newSurgeon.specialty"
              type="text"
              placeholder="Örn: Genel Cerrahi, Kalp Damar, Ortopedi"
              required
            />
          </div>

          <div class="form-group">
            <label for="offDay">İzinli Gün (İsteğe Bağlı)</label>
            <select id="offDay" v-model="newSurgeon.off_day" class="styled-select">
              <option value="">İzin Günü Yok</option>
              <option v-for="d in daysOfWeek" :key="d.value" :value="d.value">
                {{ d.label }}
              </option>
            </select>
          </div>

          <button type="submit" class="btn-primary" :disabled="submitting">
            <span v-if="submitting">Ekleniyor...</span>
            <span v-else>+ Cerrah Ekle</span>
          </button>
        </form>
      </div>

      <!-- SAĞ: CERRAH LİSTESİ TABLOSU -->
      <div class="card list-card">
        <div class="card-header space-between">
          <div class="title-with-icon">
            <div class="icon-wrapper">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
            </div>
            <h3>Kayıtlı Cerrahlar</h3>
          </div>
          <span class="count-badge">{{ surgeons.length }} Cerrah</span>
        </div>

        <div v-if="loading" class="state-container">
          <div class="spinner"></div>
          <p>Yükleniyor...</p>
        </div>

        <div v-else-if="error" class="state-container error">
          <p>{{ error }}</p>
        </div>

        <div v-else-if="surgeons.length > 0" class="table-wrapper">
          <table class="styled-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Doktor Adı</th>
                <th>Uzmanlık Alanı</th>
                <th>İzin Günü</th>
                <th>Durum</th>
                <th class="text-right">İşlemler</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="surgeon in surgeons" :key="surgeon.id">
                <td class="id-cell">#{{ surgeon.id }}</td>
                <td class="name-cell">
                  <div class="avatar-icon">👨‍⚕️</div>
                  <span>{{ surgeon.name }}</span>
                </td>
                <td>
                  <span class="specialty-badge">{{ surgeon.specialty || 'Genel Cerrahi' }}</span>
                </td>
                <td>
                  <span class="offday-badge" :class="{ 'has-offday': surgeon.off_day }">
                    {{ formatDay(surgeon.off_day) }}
                  </span>
                </td>
                <td>
                  <span class="status-badge active">
                    <span class="dot"></span> Aktif
                  </span>
                </td>
                <td class="text-right">
                  <button class="btn-danger-outline" @click="handleDelete(surgeon.id)" title="Pasife Al">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    Sil
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="state-container empty">
          <div class="empty-icon">👨‍⚕️</div>
          <p>Henüz kayıtlı bir cerrah bulunmuyor.</p>
          <small>Soldaki form üzerinden yeni bir cerrah ekleyebilirsiniz.</small>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  color: #1e293b;
}

.page-header {
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

.content-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 24px;
  align-items: start;
}

@media (max-width: 900px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
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

.styled-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.form-group input,
.styled-select {
  padding: 10px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
  outline: none;
  background-color: #fff;
}

.form-group input:focus,
.styled-select:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}

.btn-primary {
  background: #2563eb;
  color: white;
  border: none;
  padding: 11px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s ease;
  width: 100%;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-primary:disabled {
  background: #94a3b8;
  cursor: not-allowed;
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
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: #0f172a;
}

.avatar-icon {
  font-size: 18px;
}

.specialty-badge {
  background: #f0fdf4;
  color: #166534;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid #bbf7d0;
}

.offday-badge {
  background: #f8fafc;
  color: #64748b;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid #e2e8f0;
}

.offday-badge.has-offday {
  background: #fff7ed;
  color: #c2410c;
  border-color: #ffedd5;
  font-weight: 600;
}

.text-right {
  text-align: right;
}

.status-badge.active {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #dcfce7;
  color: #15803d;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
}

.status-badge .dot {
  width: 6px;
  height: 6px;
  background: #22c55e;
  border-radius: 50%;
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
</style>