<template>
  <div v-if="isOpen" class="modal-backdrop" @click.self="close">
    <div class="modal-card">
      <div class="modal-header">
        <h3>📋 Ameliyat Detayları</h3>
        <button type="button" class="close-btn" @click="close">&times;</button>
      </div>

      <div class="modal-body" v-if="operation">
        <!-- Hasta Adı -->
        <div class="detail-row">
          <span class="label">Hasta Adı:</span>
          <span class="value strong">{{ operation.patient_name || 'Belirtilmedi' }}</span>
        </div>

        <!-- Ameliyat Türü -->
        <div class="detail-row">
          <span class="label">Ameliyat Türü:</span>
          <span class="value">{{ operation.operation_name || 'Belirtilmedi' }}</span>
        </div>

        <!-- Cerrah / Doktor (Null gelse de görünür) -->
        <div class="detail-row">
          <span class="label">Atanan Cerrah:</span>
          <span class="value" :class="{ 'not-assigned': !getSurgeonName(operation) }">
            👨‍⚕️ {{ getSurgeonName(operation) || 'Atanmadı' }}
          </span>
        </div>

        <!-- Anestezi Ekibi (Null gelse de görünür) -->
        <div class="detail-row">
          <span class="label">Anestezi Ekibi:</span>
          <span class="value" :class="{ 'not-assigned': !getAnesthesiaName(operation) }">
            💉 {{ getAnesthesiaName(operation) || 'Atanmadı' }}
          </span>
        </div>

        <!-- Öncelik Durumu -->
        <div class="detail-row">
          <span class="label">Öncelik Durumu:</span>
          <span class="badge" :class="operation.priority?.toLowerCase()">
            {{ operation.priority || 'NORMAL' }}
          </span>
        </div>

        <!-- Gerekli Branş -->
        <div class="detail-row">
          <span class="label">Gerekli Branş:</span>
          <span class="value">{{ operation.required_specialty || 'Belirtilmedi' }}</span>
        </div>

        <!-- Tahmini Süre -->
        <div class="detail-row">
          <span class="label">Tahmini Süre:</span>
          <span class="value">⏱️ {{ (operation.duration_slot || 1) * 30 }} dakika</span>
        </div>

        <!-- Atanan Salon (OR-1, OR-2 Akıllı Eşleşme) -->
        <div class="detail-row">
          <span class="label">Atanan Salon:</span>
          <span class="value highlight-room">{{ resolvedRoomName }}</span>
        </div>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn-close" @click="close">Kapat</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  operation: {
    type: Object,
    default: null
  },
  rooms: {
    type: Array,
    default: () => []
  },
  // İleride doktor ve anestezi listesini geçmek istersen hazır olsun:
  surgeons: {
    type: Array,
    default: () => []
  },
  anesthesiaTeams: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}

// Cerrah ID / Obje / Isım Formatlayıcı
const getSurgeonName = (op) => {
  if (!op) return null
  const val = op.surgeon || op.surgeon_name || op.doctor || op.doctor_name || op.assigned_surgeon
  if (!val || val === 'null') return null

  // 1. Eğer Obje olarak geldiyse (örn: { id: 7, name: "Dr. Ahmet" })
  if (typeof val === 'object') {
    return val.name || val.full_name || val.username || `Dr. #${val.id}`
  }

  // 2. Eğer surgeons dizisi props olarak geldiyse ID ile eşleştir
  if (props.surgeons && props.surgeons.length > 0) {
    const found = props.surgeons.find(s => String(s.id) === String(val))
    if (found) return found.name || found.full_name
  }

  // 3. Eğer sadece sayısal ID geldiyse (örn: 7)
  if (!isNaN(val)) {
    return `Dr. #${val}`
  }

  return val
}

// Anestezi ID / Obje / Isım Formatlayıcı
const getAnesthesiaName = (op) => {
  if (!op) return null
  const val = op.anesthesia || op.anesthesia_team || op.anesthesiologist || op.anesthesia_name
  if (!val || val === 'null') return null

  // 1. Eğer Obje olarak geldiyse
  if (typeof val === 'object') {
    return val.name || val.full_name || val.team_name || `Anestezi Ekibi #${val.id}`
  }

  // 2. Eğer anesthesiaTeams dizisi props olarak geldiyse ID ile eşleştir
  if (props.anesthesiaTeams && props.anesthesiaTeams.length > 0) {
    const found = props.anesthesiaTeams.find(a => String(a.id) === String(val))
    if (found) return found.name || found.team_name
  }

  // 3. Eğer sadece sayısal ID geldiyse (örn: 6)
  if (!isNaN(val)) {
    return `Anestezi Ekibi #${val}`
  }

  return val
}

// Salon İsmi Eşleştirme
const resolvedRoomName = computed(() => {
  if (!props.operation) return 'Atanmadı'
  const op = props.operation

  if (op.room && typeof op.room === 'object') return op.room.name || op.room.room_name
  if (op.room_name) return op.room_name

  const targetRoomId = op.calculatedRoomId || op.required_room || op.room_id || op.room

  if (props.rooms && props.rooms.length > 0 && targetRoomId) {
    const foundRoom = props.rooms.find(r => String(r.id) === String(targetRoomId))
    if (foundRoom) return foundRoom.name || foundRoom.room_name

    const indexBasedRoom = props.rooms.find((r, idx) => idx === (Number(targetRoomId) % props.rooms.length))
    if (indexBasedRoom) return indexBasedRoom.name || indexBasedRoom.room_name
  }

  return targetRoomId ? `OR-${targetRoomId}` : 'Atanmadı'
})
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.modal-card {
  background: #ffffff;
  width: 90%;
  max-width: 480px;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.modal-header {
  padding: 16px 20px;
  background-color: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #1e293b;
}
.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #64748b;
  cursor: pointer;
}
.modal-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  padding-bottom: 8px;
  border-bottom: 1px dashed #f1f5f9;
}
.label {
  color: #64748b;
  font-weight: 500;
}
.value {
  color: #0f172a;
  font-weight: 600;
}
.value.not-assigned {
  color: #94a3b8;
  font-weight: 400;
  font-style: italic;
}
.highlight-room {
  color: #0284c7;
  font-weight: 700;
}
.badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
}
.badge.critical, .badge.high { background-color: #fee2e2; color: #991b1b; }
.badge.normal, .badge.medium { background-color: #e0f2fe; color: #075985; }
.modal-footer {
  padding: 12px 20px;
  background-color: #f8fafc;
  border-top: 1px solid #e2e8f0;
  text-align: right;
}
.btn-close {
  padding: 8px 16px;
  background-color: #0284c7;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}
.btn-close:hover { background-color: #0369a1; }
</style>