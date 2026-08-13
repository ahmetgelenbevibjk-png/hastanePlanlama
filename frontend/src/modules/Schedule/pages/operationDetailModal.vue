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

        <!-- Atanan Cerrah -->
        <div class="detail-row">
          <span class="label">Atanan Cerrah:</span>
          <span class="value" :class="{ 'not-assigned': !surgeonDisplay }">
            👨‍⚕️ {{ surgeonDisplay || 'Atanmadı' }}
          </span>
        </div>

        <!-- Anestezi Ekibi -->
        <div class="detail-row">
          <span class="label">Anestezi Ekibi:</span>
          <span class="value" :class="{ 'not-assigned': !anesthesiaDisplay }">
            💉 {{ anesthesiaDisplay || 'Atanmadı' }}
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

        <!-- Atanan Salon -->
        <div class="detail-row">
          <span class="label">Atanan Salon:</span>
          <span class="value highlight-room">{{ roomDisplay }}</span>
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
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}

// Cerrah İsmi Mantığı
const surgeonDisplay = computed(() => {
  if (!props.operation) return null
  const op = props.operation

  // 1. Backend'den metin olarak gelen isim
  if (op.surgeon_name) return op.surgeon_name
  if (op.doctor_name) return op.doctor_name

  // 2. Obje olarak gelen cerrah verisi
  if (op.surgeon && typeof op.surgeon === 'object') {
    return op.surgeon.name || op.surgeon.full_name || op.surgeon.username
  }

  // 3. Doğrudan metin geldiyse
  if (typeof op.surgeon === 'string' && isNaN(op.surgeon)) {
    return op.surgeon
  }

  return null
})

// Anestezi İsmi Mantığı
const anesthesiaDisplay = computed(() => {
  if (!props.operation) return null
  const op = props.operation

  if (op.anesthesia_name) return op.anesthesia_name

  if (op.anesthesia && typeof op.anesthesia === 'object') {
    return op.anesthesia.name || op.anesthesia.team_name
  }

  if (typeof op.anesthesia === 'string' && isNaN(op.anesthesia)) {
    return op.anesthesia
  }

  return null
})

// Salon İsmi Mantığı
const roomDisplay = computed(() => {
  if (!props.operation) return 'Atanmadı'
  const op = props.operation

  if (op.room_name) return op.room_name
  if (op.room && typeof op.room === 'object') return op.room.name || op.room.room_name

  const targetRoomId = op.calculatedRoomId || op.required_room || op.room_id || op.room

  if (props.rooms && props.rooms.length > 0 && targetRoomId) {
    const foundRoom = props.rooms.find(r => String(r.id) === String(targetRoomId))
    if (foundRoom) return foundRoom.name || foundRoom.room_name
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