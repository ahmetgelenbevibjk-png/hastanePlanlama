<script setup>
import { ref } from 'vue'

defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  candidates: {
    type: Array,
    default: () => []
  },
  selectedCandidateId: [Number, String]
})

const emit = defineEmits(['close', 'select-plan'])

// Hangi adayın ceza detayının açık olduğunu takip eden state
const activePenaltyId = ref(null)

const togglePenaltyBreakdown = (id) => {
  if (activePenaltyId.value === id) {
    activePenaltyId.value = null
  } else {
    activePenaltyId.value = id
  }
}

const close = () => {
  activePenaltyId.value = null
  emit('close')
}

const selectPlan = (candidate) => {
  emit('select-plan', candidate)
  close()
}

const getScoreBadgeClass = (score) => {
  if (score >= 85) return 'badge-success'
  if (score >= 60) return 'badge-warning'
  return 'badge-danger'
}
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="close">
    <div class="modal-container">
      <div class="modal-header">
        <h3>Optimized Aday Planlar ({{ candidates?.length || 0 }})</h3>
        <button class="btn-close" @click="close">&times;</button>
      </div>

      <div class="modal-body">
        <div
          v-for="candidate in candidates"
          :key="candidate.candidate_id || candidate.id"
          class="candidate-card-wrapper"
        >
          <div
            class="candidate-card"
            :class="{ 'is-selected': selectedCandidateId === (candidate.candidate_id || candidate.id) }"
          >
            <div class="card-details">
              <div class="card-title-row">
                <h4>{{ candidate.strategy_name || 'Alternatif Senaryo' }}</h4>
                <div class="score-container">
                  <span class="badge" :class="getScoreBadgeClass(candidate.fitness_score)">
                    %{{ candidate.fitness_score }} Başarı
                  </span>

                  <!-- Skor Kırılımı Bilgi Butonu -->
                  <button
                    class="btn-info"
                    title="Skor Kırılımını Göster"
                    @click.stop="togglePenaltyBreakdown(candidate.candidate_id || candidate.id)"
                  >
                    ℹ️
                  </button>
                </div>
              </div>

              <div class="card-stats">
                <span>✅ Atanan: <strong>{{ candidate.assigned_count }}</strong></span>
                <span>❌ Atanamayan: <strong>{{ candidate.unassigned_count }}</strong></span>
                <span>⚠️ Toplam Ceza: <strong>{{ candidate.total_penalty }}</strong></span>
              </div>
            </div>

            <button
              class="btn-apply"
              :disabled="selectedCandidateId === (candidate.candidate_id || candidate.id)"
              @click="selectPlan(candidate)"
            >
              {{ selectedCandidateId === (candidate.candidate_id || candidate.id) ? 'Aktif Çizelge' : 'Çizelgeye Yükle' }}
            </button>
          </div>

          <!-- Ceza Detay Alanı (Penalty Breakdown Popover / Panel) -->
          <div
            v-if="activePenaltyId === (candidate.candidate_id || candidate.id)"
            class="penalty-breakdown-panel"
          >
            <div class="breakdown-header">
              <span>📊 Puan Kırılma Sebepleri</span>
              <button class="btn-mini-close" @click="activePenaltyId = null">&times;</button>
            </div>

            <ul v-if="candidate.penalties && candidate.penalties.length > 0" class="breakdown-list">
              <li v-for="(item, index) in candidate.penalties" :key="index" class="breakdown-item">
                <span class="reason">{{ item.reason }}</span>
                <span class="penalty-points">-{{ item.points }} Puan</span>
              </li>
            </ul>
            <div v-else class="no-penalties">
              Bu senaryoda uygulanan ek ceza kısıtı bulunmamaktadır.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.modal-container {
  background: #ffffff;
  width: 90%;
  max-width: 650px;
  max-height: 80vh;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.15rem;
  color: #0f172a;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #64748b;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.candidate-card-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.candidate-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 14px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s ease;
  background: #fff;
}

.candidate-card.is-selected {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}

.card-title-row h4 {
  margin: 0;
  font-size: 1rem;
  color: #1e293b;
}

.score-container {
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-info {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-info:hover {
  background: #e2e8f0;
}

.card-stats {
  display: flex;
  gap: 15px;
  font-size: 0.88rem;
  color: #475569;
}

.badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: bold;
}
.badge-success { background: #dcfce7; color: #15803d; }
.badge-warning { background: #fef9c3; color: #a16207; }
.badge-danger { background: #fee2e2; color: #b91c1c; }

.btn-apply {
  padding: 8px 14px;
  border-radius: 6px;
  border: none;
  background: #2563eb;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-apply:hover:not(:disabled) {
  background: #1d4ed8;
}
.btn-apply:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

/* Ceza Detay Paneli Stilleri */
.penalty-breakdown-panel {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #ef4444;
  border-radius: 6px;
  padding: 10px 14px;
  font-size: 0.85rem;
  animation: fadeIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

.breakdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #334155;
  margin-bottom: 6px;
}

.btn-mini-close {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #94a3b8;
}

.breakdown-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  color: #475569;
}

.penalty-points {
  color: #dc2626;
  font-weight: 600;
}

.no-penalties {
  color: #64748b;
  font-style: italic;
}
</style>