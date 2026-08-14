<template>
  <div v-if="isOpen" class="modal-backdrop" @click.self="close">
    <div class="modal-card">
      <div class="modal-header">
        <h3>➕ Yeni Operasyon Ekle</h3>
        <button class="btn-close" type="button" @click="close">✕</button>
      </div>

      <form @submit.prevent="handleCreate" class="styled-form">
        <div class="form-group">
          <label for="patientName">Hasta Adı Soyadı</label>
          <input
            id="patientName"
            v-model="newOperation.patient_name"
            type="text"
            placeholder="Örn: Ahmet Yılmaz"
            required
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="opName">Operasyon Adı / Tanımı</label>
          <input
            id="opName"
            v-model="newOperation.operation_name"
            type="text"
            placeholder="Örn: Açık Kalp Ameliyatı"
            required
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="specialty">Gerekli Uzmanlık / Branş</label>
          <input
            id="specialty"
            v-model="newOperation.required_specialty"
            type="text"
            placeholder="Örn: Kalp ve Damar Cerrahisi"
            required
            class="form-input"
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="duration">Tahmini Süre (Dakika)</label>
            <input
              id="duration"
              v-model.number="newOperation.duration"
              type="number"
              placeholder="Örn: 120"
              min="15"
              step="15"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="priority">Öncelik Seviyesi</label>
            <select id="priority" v-model="newOperation.priority" class="styled-select">
              <option value="LOW">Düşük</option>
              <option value="MEDIUM">Normal</option>
              <option value="HIGH">Acil / Yüksek</option>
              <option value="CRITICAL">Kritik 🚨</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="surgeon">Sorumlu Cerrah (İsteğe Bağlı)</label>
          <select id="surgeon" v-model="newOperation.surgeon" class="styled-select">
            <option value="">Otomatik Atansın (Algoritma)</option>
            <option v-for="s in surgeons" :key="s.id" :value="s.id">
              {{ s.name }} ({{ s.specialty || 'Branş Belirtilmemiş' }})
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="anesthesia">Anestezi Ekibi (İsteğe Bağlı)</label>
          <select id="anesthesia" v-model="newOperation.anesthesia_team" class="styled-select">
            <option value="">Otomatik Atansın (Algoritma)</option>
            <option v-for="a in anesthesiaTeams" :key="a.id" :value="a.id">
              {{ a.name }}
            </option>
          </select>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-secondary" @click="close">
            İptal
          </button>
          <button type="submit" class="btn-primary" :disabled="submitting">
            <span v-if="submitting">Ekleniyor...</span>
            <span v-else>Operasyon Ekle</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { operationService } from '@/modules/Operations/services/operationService'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  surgeons: {
    type: Array,
    default: () => []
  },
  anesthesiaTeams: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'created'])

const submitting = ref(false)
const newOperation = ref({
  patient_name: '',
  operation_name: '',
  required_specialty: '',
  duration: 60,
  priority: 'MEDIUM',
  surgeon: '',
  anesthesia_team: ''
})

const close = () => {
  newOperation.value = {
    patient_name: '',
    operation_name: '',
    required_specialty: '',
    duration: 60,
    priority: 'MEDIUM',
    surgeon: '',
    anesthesia_team: ''
  }
  emit('close')
}

const handleCreate = async () => {
  if (!newOperation.value.operation_name.trim()) return

  submitting.value = true

  const calculatedSlots = Math.ceil((newOperation.value.duration || 30) / 30)

  const payload = {
    patient_name: newOperation.value.patient_name,
    operation_name: newOperation.value.operation_name,
    required_specialty: newOperation.value.required_specialty,
    duration_slot: calculatedSlots,
    priority: newOperation.value.priority,
    surgeon: newOperation.value.surgeon || null,
    anesthesia: newOperation.value.anesthesia_team || null
  }

  try {
    await operationService.create(payload)
    emit('created')
    close()
  } catch (err) {
    if (err.response && err.response.data) {
      alert('Operasyon eklenirken hata: ' + JSON.stringify(err.response.data))
    } else {
      alert('Operasyon eklenirken hata oluştu!')
    }
    console.error(err)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: #ffffff;
  border-radius: 12px;
  width: 100%;
  max-width: 520px;
  padding: 24px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
}

.btn-close {
  background: transparent;
  border: none;
  font-size: 18px;
  color: #94a3b8;
  cursor: pointer;
  transition: color 0.2s;
}

.btn-close:hover {
  color: #0f172a;
}

.styled-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
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

.form-input,
.styled-select {
  padding: 10px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s ease;
  background-color: #fff;
}

.form-input:focus,
.styled-select:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-secondary:hover {
  background: #e2e8f0;
}

.btn-primary {
  background: #2563eb;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-primary:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}
</style>