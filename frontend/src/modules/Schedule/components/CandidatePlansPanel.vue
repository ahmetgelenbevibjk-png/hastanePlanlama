<script setup>
const props= defineProps({
  candidates: {
    type:Array,
    default:()=> []
  },
  selectedPlanId: {
    type:[Number,String],
    default:null
  }
})

const emit =defineEmits(['select-plan'])

const selectPlan =(plan)=> {
  emit('select-plan',plan)
}
const getScoreClass=(score)=> {
    if (score>=80)return 'score-high'
    if (score>=50) return 'score-medium'
    return 'score-low'
  }

</script>

<template>
<div v-if="candidates && candidates.length > 0" class="candidates-panel">
    <div class="panel-header">
      <div class="header-title">
        <h3>Denenen Alternatif Planlar</h3>
        <span class="subtitle">Algoritmanın simüle ettiği senaryoları karşılaştırıp çizelgeye yükleyebilirsiniz.</span>
      </div>
    </div>

    <div class="candidates-grid">
      <div
        v-for="plan in candidates"
        :key="plan.id"
        :class="['candidate-card', { active: selectedPlanId === plan.id }]"
        @click="selectPlan(plan)"
      >
        <div class="card-header">
          <span class="plan-title">{{ plan.name }}</span>
          <span :class="['fitness-badge', getScoreClass(plan.fitness_score)]">
            %{{ plan.fitness_score }}
          </span>
        </div>

        <div class="card-body">
          <div class="stat-row">
            <span class="label">Yerleşen:</span>
            <span class="value text-success">{{ plan.assigned_count }} Operasyon</span>
          </div>
          <div class="stat-row" v-if="plan.unassigned_count > 0">
            <span class="label">Açıkta Kalan:</span>
            <span class="value text-danger">{{ plan.unassigned_count }} Operasyon</span>
          </div>
          <div class="stat-row">
            <span class="label">Toplam Ceza:</span>
            <span class="value">{{ plan.total_penalty }} Puan</span>
          </div>
        </div>

        <div class="card-footer">
          <span class="action-text">
            {{ selectedPlanId === plan.id ? '✓ Aktif Plan' : 'Çizelgeye Yükle →' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.candidates-panel {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.panel-header {
  margin-bottom: 16px;
}

.panel-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #1e293b;
  font-weight: 700;
}

.subtitle {
  font-size: 0.85rem;
  color: #64748b;
}

.candidates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.candidate-card {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.candidate-card:hover {
  border-color: #3b82f6;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.candidate-card.active {
  border-color: #2563eb;
  background: #eff6ff;
  box-shadow: 0 0 0 1px #2563eb;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.plan-title {
  font-weight: 600;
  font-size: 0.9rem;
  color: #0f172a;
}

.fitness-badge {
  font-size: 0.8rem;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 6px;
}

.score-high {
  background: #dcfce7;
  color: #15803d;
}

.score-medium {
  background: #fef3c7;
  color: #b45309;
}

.score-low {
  background: #fee2e2;
  color: #b91c1c;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.82rem;
  margin-bottom: 12px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
}

.label {
  color: #64748b;
}

.value {
  font-weight: 600;
  color: #334155;
}

.text-success { color: #16a34a; }
.text-danger { color: #dc2626; }

.card-footer {
  border-top: 1px solid #e2e8f0;
  padding-top: 8px;
  text-align: right;
}

.action-text {
  font-size: 0.8rem;
  font-weight: 600;
  color: #2563eb;
}
</style>