<script setup>
import {ref , onMounted} from 'vue'
import {anesthesiaService } from '../services/anesthesiaService'

const teams=ref([])
const loading= ref(false)
const submitting=ref(false)
const error= ref(null)

const newTeam=ref({
  name:'',
  shift:''
})

const fetchTeams=async ()=> {
  loading.value=true
  error.value=null
  try{
    const response =await anesthesiaService.getAll()
    teams.value =response.data
  }catch(err){
    error.value='Anestezi ekipleri yüklenirken hata oluştu.'
    console.error(err)
  }finally{
    loading.value=false
  }
}

const handleCreate= async () => {
  if(!newTeam.value.name.trim()) return

  submitting.value=true
  try {
    await anesthesiaService.create(newTeam.value)
    newTeam.value={name:'',shift:''}
    await fetchTeams()
  }catch(err) {
    alert('Ekip eklenirken hata oluştu!')
    console.error(err)
  } finally {
    submitting.value =false
  }
}

const handDelete= async(id)=> {
  if(!confirm('Bu anestezi ekibini pasife almak istediğinize emin misiniz?')) return

  try{
    await anesthesiaService.delete(id)
    await fetchTeams()
  }catch (err) {
    alert('Silme işlemi başarısız.')
    console.error(err)
  }
}

onMounted(() => {
  fetchTeams()
})


</script>

<template>
<div class="page-container">
    <!-- BAŞLIK SEKSİYONU -->
    <div class="page-header">
      <div>
        <h2>Anestezi Ekipleri Yönetimi</h2>
        <p class="subtitle">Sistemdeki anestezi doktorlarını ve tekniker ekiplerini yönetin.</p>
      </div>
    </div>

    <div class="content-grid">
      <!-- SOL: YENİ ANESTEZİ EKİBİ EKLEME FORMU -->
      <div class="card form-card">
        <div class="card-header">
          <div class="icon-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49 0 2.81.47 3.84 1.25M1 14c1.03-.78 2.35-1.25 3.84-1.25M12 2a4 4 0 0 0-4 4v2a4 4 0 0 0 8 0V6a4 4 0 0 0-4-4z"></path><path d="M18 14.28V14a6 6 0 0 0-12 0v.28"></path></svg>
          </div>
          <h3>Yeni Ekip Ekle</h3>
        </div>

        <form @submit.prevent="handleCreate" class="styled-form">
          <div class="form-group">
            <label for="teamName">Ekip / Sorumlu Adı</label>
            <input
              id="teamName"
              v-model="newTeam.name"
              type="text"
              placeholder="Örn: Anestezi Ekibi A (Dr. Mehmet)"
              required
            />
          </div>

          <div class="form-group">
            <label for="shift">Vardiya / Çalışma Saatleri</label>
            <input
              id="shift"
              v-model="newTeam.shift"
              type="text"
              placeholder="Örn: 08:00 - 16:00"
            />
          </div>

          <button type="submit" class="btn-primary" :disabled="submitting">
            <span v-if="submitting">Ekleniyor...</span>
            <span v-else>+ Ekip Ekle</span>
          </button>
        </form>
      </div>

      <!-- SAĞ: ANESTEZİ EKİPLERİ LİSTESİ -->
      <div class="card list-card">
        <div class="card-header space-between">
          <div class="title-with-icon">
            <div class="icon-wrapper">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
            </div>
            <h3>Kayıtlı Anestezi Ekipleri</h3>
          </div>
          <span class="count-badge">{{ teams.length }} Ekip</span>
        </div>

        <div v-if="loading" class="state-container">
          <div class="spinner"></div>
          <p>Yükleniyor...</p>
        </div>

        <div v-else-if="error" class="state-container error">
          <p>{{ error }}</p>
        </div>

        <div v-else-if="teams.length > 0" class="table-wrapper">
          <table class="styled-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Ekip Adı</th>
                <th>Vardiya</th>
                <th>Durum</th>
                <th class="text-right">İşlemler</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="team in teams" :key="team.id">
                <td class="id-cell">#{{ team.id }}</td>
                <td class="name-cell">
                  <div class="avatar-icon">💉</div>
                  <span>{{ team.name }}</span>
                </td>
                <td>
                  <span class="shift-badge">{{ team.shift || 'Tam Zamanlı' }}</span>
                </td>
                <td>
                  <span class="status-badge active">
                    <span class="dot"></span> Aktif
                  </span>
                </td>
                <td class="text-right">
                  <button class="btn-danger-outline" @click="handleDelete(team.id)" title="Pasife Al">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    Sil
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="state-container empty">
          <div class="empty-icon">💉</div>
          <p>Henüz kayıtlı bir anestezi ekibi bulunmuyor.</p>
          <small>Soldaki form üzerinden yeni bir ekip ekleyebilirsiniz.</small>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  max-width:1200px;
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
  margin: 0 0 6px 0 ;
}

.subtitle {
  color: #64748b;
  font-size:14px;
  margin: 0 ;
}

.content-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 24px;
  align-items:start;
}

@media( max-width:900px) {
  .content-grid {
    grid-template-columns:1fr;
  }
}

.card {
  background: #ffffff;
  border-radius:12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
  padding:24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap:12px;
  margin-bottom:16px;
  border-bottom:1px solid #f1f5f9;
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
  font-weight:600;
  color: #1e293b;
  margin: 0 ;
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
  color:#475569;
  font-size: 12px;
  font-weight:600;
  padding: 4px 10px;
  border-radius:20px
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

.form-group input {
  padding:10px 14px;
  border:1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
  outline: none ;
}

.form-group input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.15);
}

.btn-primary {
  background: #2563eb;
  color:white;
  border:none;
  padding: 11px 16px;
  border-radius:8px;
  font-weight:600;
  font-size: 14px;
  cursor:pointer;
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
  background:transparent;
  color: #ef4444;
  border:1px solid #fca5a5;
  padding: 6px 12px;
  border-radius:6px;
  font-size:13px;
  font-weight:500;
  cursor:pointer;
  display:inline-flex;
  align-items:center;
  gap:6px;
  transition:all 0.2s ease;
}

.btn-danger-outline:hover {
  background: #fef2f2;
  border-color: #ef4444;
}

.table-wrapper {
  overflow-x:auto;
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

.shift-badge {
  background: #f0fdf4;
  color: #166534;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid #bbf7d0;
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