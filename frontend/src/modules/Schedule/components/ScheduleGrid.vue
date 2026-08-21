<template>
  <div class="schedule-grid-container">
    
    <div class="table-wrapper">
      <table class="timeline-table">
        <thead>
          <tr>
            <th class="room-column">Salon / Slot</th>
            <th v-for="slot in TIME_SLOTS" :key="slot.time" class="time-header">
              {{ slot.time }}
            </th>
          </tr>
        </thead>
        <tbody>
          <!-- Salonlar Listesi -->
          <tr v-for="room in rooms" :key="room.id">
            <td class="room-cell">
              <strong>{{ room.name || `${ROOM_CODE_PREFIX}${room.id}` }}</strong>
              <span v-if="room.specialty_type" class="room-capacity">{{ room.specialty_type }}</span>
            </td>

            <!-- 30 Dakikalık Slot Hücreleri -->
            <template v-for="slot in TIME_SLOTS" :key="slot.index">
              <!-- Performans Optimizasyonu: Metodun yüzlerce kez çalışmasını önlemek için op değişkenine sabitledik -->
              <template v-for="op in [getOpStartingAt(room.id, slot.index)]" :key="op ? op.id || op.operation_id : `empty-${slot.index}`">
                
                <!-- 1. Eğer bu slotta YENİ BAŞLAYAN bir ameliyat varsa -->
                <td
                  v-if="op"
                  :colspan="op.duration_slot || DEFAULT_SLOT_COUNT"
                  class="slot-cell occupied"
                >
                  <div
                    class="operation-card"
                    :class="getPriorityClass(op.priority)"
                    draggable="true"
                    @dragstart="handleDragStart($event, op)"
                    @click="onOperationClick(op)"
                    :title="`${op.patient_name || DEFAULT_PATIENT_NAME} - Detaylar için tıklayın`"
                  >
                    <div class="op-header">
                      <span class="op-title">
                        {{ op.patient_name || DEFAULT_PATIENT_NAME }} -
                        {{ op.operation_name || DEFAULT_OPERATION_NAME }}
                      </span>
                      <!-- Öncelik Rozeti -->
                      <span
                        v-if="op.priority"
                        class="priority-badge"
                      >
                        {{ op.priority }}
                      </span>
                    </div>

                    <div class="op-surgeon" v-if="op.surgeonDisplay">
                      👨‍⚕️ {{ op.surgeonDisplay }}
                    </div>
                    <div class="op-anesthesia" v-if="op.anesthesiaDisplay">
                      💉 {{ op.anesthesiaDisplay }}
                    </div>
                    <div class="op-duration">
                      ⏱️ {{ (op.duration_slot || DEFAULT_SLOT_COUNT) * SLOT_DURATION_MINUTES }} dk
                    </div>
                  </div>
                </td>

                <!-- 2. Eğer bu slot bir ameliyatın devamı DEĞİLSE boş td koy (Bırakma Alanı) -->
                <td
                  v-else-if="!isSlotCoveredByPreviousOp(room.id, slot.index)"
                  class="slot-cell empty"
                  :class="{ 'drag-over': isDragOver(room.id, slot.index) }"
                  @dragover.prevent="handleDragOver(room.id, slot.index)"
                  @dragleave="handleDragLeave"
                  @drop="handleDrop($event, room.id, slot.index)"
                ></td>
              </template>
            </template>
          </tr>

          <!-- Eğer hiç salon yoksa -->
          <tr v-if="rooms.length === 0">
            <td :colspan="TIME_SLOTS.length + 1" class="no-data">
              Henüz tanımlanmış bir ameliyathane salonu bulunmuyor.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { 
  TIME_SLOTS, 
  SLOT_DURATION_MINUTES, 
  DEFAULT_SLOT_COUNT,
  ROOM_CODE_PREFIX, 
  DEFAULT_PATIENT_NAME, 
  DEFAULT_OPERATION_NAME,
  MANUAL_UPDATE_ENDPOINT 
} from '../scheduleConstants.js'

const props = defineProps({
  date: { type: String, required: true },
  rooms: { type: Array, default: () => [] },
  operations: { type: Array, default: () => [] },
  surgeons: { type: Array, default: () => [] },
  anesthesiaTeams: { type: Array, default: () => [] }
})

const emit = defineEmits(['select-operation', 'operation-updated'])

const draggedOperation = ref(null)
const activeHoverCell = ref(null)

const onOperationClick = (operation) => {
  emit('select-operation', operation)
}

// Operasyonları Salon ve Slot Bilgilerine Göre İşleme
const processedOperations = computed(() => {
  if (!props.operations || props.operations.length === 0) return []

  return props.operations
    .filter(op => {
      const roomId = op.room_id ?? op.required_room ?? (typeof op.room === 'object' ? op.room?.id : op.room)
      const startSlot = op.start_slot ?? op.calculatedStartSlot

      return roomId !== undefined && roomId !== null && startSlot !== undefined && startSlot !== null
    })
    .map((op) => {
      const assignedRoomId = op.room_id ?? op.required_room ?? (typeof op.room === 'object' ? op.room?.id : op.room)
      const startSlot = op.start_slot ?? op.calculatedStartSlot

      let sDisplay = op.surgeon_name || op.doctor_name
      if (!sDisplay && op.surgeon) {
        if (typeof op.surgeon === 'object') sDisplay = op.surgeon.name || op.surgeon.full_name
        else if (props.surgeons && props.surgeons.length > 0) {
          const match = props.surgeons.find(s => String(s.id) === String(op.surgeon))
          if (match) sDisplay = match.name || match.full_name
        }
      }

      let aDisplay = op.anesthesia_name || op.anesthesia_team_name
      if (!aDisplay && op.anesthesia) {
        if (typeof op.anesthesia === 'object') aDisplay = op.anesthesia.name || op.anesthesia.team_name
        else if (props.anesthesiaTeams && props.anesthesiaTeams.length > 0) {
          const match = props.anesthesiaTeams.find(a => String(a.id) === String(op.anesthesia))
          if (match) aDisplay = match.name || match.team_name
        }
      }

      return {
        ...op,
        calculatedRoomId: String(assignedRoomId),
        calculatedStartSlot: Number(startSlot),
        surgeonDisplay: sDisplay,
        anesthesiaDisplay: aDisplay
      }
    })
})

const getOpStartingAt = (roomId, slotIndex) => {
  return processedOperations.value.find(op => {
    return op.calculatedRoomId === String(roomId) && op.calculatedStartSlot === Number(slotIndex)
  })
}

const isSlotCoveredByPreviousOp = (roomId, slotIndex) => {
  return processedOperations.value.some(op => {
    if (op.calculatedRoomId !== String(roomId)) return false
    const start = op.calculatedStartSlot
    const dur = Number(op.duration_slot || DEFAULT_SLOT_COUNT)

    return slotIndex > start && slotIndex < (start + dur)
  })
}

const getPriorityClass = (priority) => {
  const p = String(priority || '').toUpperCase()
  if (p === 'KRITIK' || p === 'CRITICAL') return 'priority-critical'
  if (p === 'YÜKSEK' || p === 'HIGH') return 'priority-high'
  if (p === 'DÜŞÜK' || p === 'LOW') return 'priority-low'
  return 'priority-normal'
}

// --- SÜRÜKLE - BIRAK EVENT HANDLER'LARI ---

const handleDragStart = (event, operation) => {
  draggedOperation.value = operation
  const opId = operation.id || operation.operation_id
  event.dataTransfer.setData('text/plain', String(opId))
  event.dataTransfer.effectAllowed = 'move'
}

const handleDragOver = (roomId, slotIndex) => {
  activeHoverCell.value = `${roomId}-${slotIndex}`
}

const handleDragLeave = () => {
  activeHoverCell.value = null
}

const isDragOver = (roomId, slotIndex) => {
  return activeHoverCell.value === `${roomId}-${slotIndex}`
}

const handleDrop = async (event, targetRoomId, targetSlot) => {
  activeHoverCell.value = null

  const opId = event.dataTransfer.getData('text/plain') || draggedOperation.value?.id
  if (!opId) return

  const operation = processedOperations.value.find(
    op => String(op.id || op.operation_id) === String(opId)
  )

  if (!operation) return

  // Aynı konuma bırakıldıysa işlem yapma
  if (String(operation.calculatedRoomId) === String(targetRoomId) && Number(operation.calculatedStartSlot) === Number(targetSlot)) {
    return
  }

  try {
    const response = await axios.post(MANUAL_UPDATE_ENDPOINT, {
      operation_id: operation.id || operation.operation_id,
      target_room_id: targetRoomId,
      target_slot: targetSlot,
      day_name: props.date
    })

    if (response.data.success) {
      emit('operation-updated', {
        operationId: operation.id || operation.operation_id,
        targetRoomId,
        targetSlot
      })

      alert('Ameliyat konumu başarıyla güncellendi.')
    }
  } catch (error) {
    const errorMsg = error.response?.data?.message || 'Bu konuma taşıma yapılamaz!'
    alert(`Taşıma Başarısız: ${errorMsg}`)
  } finally {
    draggedOperation.value = null
  }
}
</script>

<style scoped>
.schedule-grid-container {
  width: 100%;
  overflow-x: auto;
}
.table-wrapper {
  min-width: 1200px;
}
.timeline-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}
.timeline-table th, .timeline-table td {
  border: 1px solid #e2e8f0;
  padding: 6px;
  text-align: center;
}
.room-column {
  width: 160px;
  background-color: #f8fafc;
  font-weight: 600;
  color: #334155;
  text-align: left !important;
  padding-left: 12px !important;
}
.time-header {
  background-color: #f1f5f9;
  color: #475569;
  font-size: 0.75rem;
  font-weight: 600;
  min-width: 60px;
}
.room-cell {
  text-align: left !important;
  padding-left: 12px !important;
  background-color: #f8fafc;
}
.room-capacity {
  display: block;
  font-size: 0.7rem;
  color: #64748b;
}
.slot-cell {
  height: 75px;
  vertical-align: middle;
  padding: 2px !important;
  background-color: #ffffff;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}
.slot-cell.empty { background-color: #fafafa; }

/* Sürükleme esnasında hedeflenen hücre stili */
.slot-cell.empty.drag-over {
  background-color: #e0f2fe !important;
  border: 2px dashed #0284c7 !important;
}

.operation-card {
  padding: 6px 8px;
  border-radius: 6px;
  font-size: 0.72rem;
  text-align: left;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  gap: 3px;
  height: 100%;
  justify-content: center;
  cursor: grab;
  user-select: none;
  transition: all 0.2s ease-in-out;
}

.operation-card:active {
  cursor: grabbing;
  opacity: 0.7;
}

.operation-card.priority-critical {
  background-color: #fef2f2;
  border-left: 4px solid #ef4444;
}
.operation-card.priority-high {
  background-color: #fff7ed;
  border-left: 4px solid #f97316;
}
.operation-card.priority-normal {
  background-color: #e0f2fe;
  border-left: 4px solid #0284c7;
}
.operation-card.priority-low {
  background-color: #f0fdf4;
  border-left: 4px solid #22c55e;
}

.operation-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  filter: brightness(0.97);
}

.op-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.op-title {
  font-weight: 700;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.priority-badge {
  font-size: 0.6rem;
  font-weight: 800;
  padding: 1px 4px;
  border-radius: 4px;
  background: rgba(0,0,0,0.06);
  text-transform: uppercase;
}

.op-surgeon, .op-anesthesia, .op-duration {
  font-size: 0.68rem;
  color: #334155;
  white-space: nowrap;
}

.no-data { padding: 30px; color: #64748b; font-size: 0.9rem; }
</style>