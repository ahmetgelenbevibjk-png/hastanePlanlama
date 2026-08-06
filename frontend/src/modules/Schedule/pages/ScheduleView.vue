<script setup>
import {ref, onMounted} from 'vue';
import {ScheduleService} from '../services';
import ScheduleGrid from '../components/ScheduleGrid.vue';

const rooms=ref ([]);
const operations=ref([]);
const loading =ref(false);
const error=ref('');

const fetchScheduleData =async ()=> {
  try {
    const [roomsRes, opsRes]=await Promise.all([
        ScheduleService.getRooms(),
        ScheduleService.getOperations(),
    ]);
    rooms.value=roomsRes.Data;
    operations.value =opsRes.Data;
  }catch(err){
    error.value='veriler yüklenirken bir hata oluştu.';
  }
};

const handleRunOptimization =async () =>{
  loading.value =true;
  error.value= '';
  try {
    await ScheduleService.runScheduler();
    await fetchScheduleData();
  }catch (err) {
    error.value = err.response?.data?.detail || 'Planlama algoritması çalıştırılamadı.';
  }finally {
    loading.value=false;
  }
};
</script>

<template>
<div class="schedule-page">
  <header class="page-header">
    <h2>Ameliyathane Günlük PlanlamaÇizelgesi</h2>
    <button @click="handleRunOptimization":disabled="loading" class="btn-primary">
      {{loading ? 'Hesaplanıyor...':' Planlamayı Çalıştır'}}
    </button>
  </header>

  <div v-if="error" class="error-banner">{{error}}</div>

<ScheduleGrid :rooms="rooms" :operations="operations" />
</div>

</template>

<style scoped>
.schedule-page {padding: 24px;}
.page-header{
  display:flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom:24px;
}
.btn-primary {
  background:#2563eb;
  color: #fff;
  padding:10px 20px;
  border-radius:6px;
  border:none;
  font-weight:600;
  cursor:pointer;
}
.btn-primary:disabled{
  background: #94a3b8;
  cursor:not-allowed;
}
.error-banner { background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fca5a5;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 16px;
}

</style>