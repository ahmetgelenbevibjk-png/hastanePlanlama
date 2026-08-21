<template>
  <div class="schedule-container">
    <h2>Ameliyat Planlama Çizelgesi (Sürükle - Bırak)</h2>

    <div class="grid-table">
      <!-- Sol Sütun: Saat Slotları -->
      <div class="time-column">
        <div class="header-cell">Saat / Slot</div>
        <div 
          v-for="slot in TIME_SLOTS" 
          :key="slot.index" 
          class="time-cell"
        >
          Slot {{ slot.index }} ({{ slot.time }})
        </div>
      </div>

      <!-- Ameliyathane Sütunları -->
      <div 
        v-for="room in activeRooms" 
        :key="room.id" 
        class="room-column"
      >
        <!-- Salon Başlığı -->
        <div class="header-cell room-header">
          {{ room.name }}
        </div>

        <!-- Slot Hücreleri -->
        <template v-for="slot in TIME_SLOTS" :key="slot.index">
          <!-- Performans Optimizasyonu: getOperationAt sonucunu op değişkenine sabitledik -->
          <template v-for="op in [getOperationAt(room.id, slot.index)]" :key="op ? op.id : `empty-${slot.index}`">
            
            <!-- 1. Ameliyatın Başladığı Slot (Kart Yüksekliği Süreye Göre Dinamiktir) -->
            <div 
              v-if="op"
              class="slot-cell occupied"
              :style="{ height: `${(op.duration_slot || 1) * SLOT_HEIGHT_PX}px` }"
            >
              <div 
                class="operation-card"
                draggable="true"
                @dragstart="handleDragStart($event, op)"
              >
                <div class="card-header">
                  <strong>{{ op.operation_name || DEFAULT_OPERATION_NAME }}</strong>
                </div>
                <div class="card-body">
                  <span>Cerrah: {{ op.surgeon_name || DEFAULT_SURGEON_NAME }}</span>
                  <span>Süre: {{ op.duration_slot || 1 }} Slot ({{ (op.duration_slot || 1) * SLOT_DURATION_MINUTES }} dk)</span>
                </div>
              </div>
            </div>

            <!-- 2. Ameliyatın Devam Ettiği Kapalı Slotlar (Çizilmez) -->
            <template v-else-if="isSlotCoveredByOperation(room.id, slot.index)"></template>

            <!-- 3. Boş Slotlar (Bırakma Alanları) -->
            <div 
              v-else
              class="slot-cell empty"
              :class="{ 'drag-over': isDragOver(room.id, slot.index) }"
              @dragover.prevent="handleDragOver(room.id, slot.index)"
              @dragleave="handleDragLeave"
              @drop="handleDrop($event, room.id, slot.index)"
            ></div>
          </template>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { 
  TIME_SLOTS, 
  SLOT_DURATION_MINUTES, 
  SLOT_HEIGHT_PX,
  DEFAULT_OPERATION_NAME, 
  DEFAULT_SURGEON_NAME,
  MSG_UPDATE_SUCCESS,
  MSG_UPDATE_ERROR,
  MANUAL_UPDATE_ENDPOINT,
  MOCK_ROOMS,
  MOCK_OPERATIONS
} from '../constants/scheduleConstants.js'

const props = defineProps({
  date: { type: String, required: true },
  rooms: { type: Array, default: () => [] },
  operations: { type: Array, default: () => [] }
})

const emit = defineEmits(['operation-updated'])

const draggedOperation = ref(null)
const activeHoverCell = ref(null)

const activeRooms = computed(() => props.rooms.length > 0 ? props.rooms : MOCK_ROOMS)
const activeOperations = computed(() => props.operations.length > 0 ? props.operations : MOCK_OPERATIONS)

// Ameliyatın başladığı ilk slotu bulur
const getOperationAt = (roomId, slotIdx) => {
  return activeOperations.value.find(
    op => Number(op.room_id) === Number(roomId) && Number(op.start_slot) === Number(slotIdx)
  )
}

// Ameliyatın kapsadığı sonraki slotların doluluğunu denetler
const isSlotCoveredByOperation = (roomId, slotIdx) => {
  return activeOperations.value.some(op => {
    if (Number(op.room_id) !== Number(roomId)) return false
    const start = Number(op.start_slot)
    const duration = Number(op.duration_slot || 1)
    return slotIdx > start && slotIdx < (start + duration)
  })
}

const handleDragStart = (event, operation) => {
  draggedOperation.value = operation
  event.dataTransfer.setData('text/plain', String(operation.id))
  event.dataTransfer.effectAllowed = 'move'
}

const handleDragOver = (roomId, slotIdx) => {
  activeHoverCell.value = `${roomId}-${slotIdx}`
}

const handleDragLeave = () => {
  activeHoverCell.value = null
}

const isDragOver = (roomId, slotIdx) => {
  return activeHoverCell.value === `${roomId}-${slotIdx}`
}

const handleDrop = async (event, targetRoomId, targetSlot) => {
  activeHoverCell.value = null 
  
  const opId = event.dataTransfer.getData('text/plain') || draggedOperation.value?.id
  if (!opId) return

  const operation = activeOperations.value.find(op => String(op.id) === String(opId))
  if (!operation) return

  if (Number(operation.room_id) === Number(targetRoomId) && Number(operation.start_slot) === Number(targetSlot)) {
    return
  }

  try {
    const response = await axios.post(MANUAL_UPDATE_ENDPOINT, {
      operation_id: operation.id,
      target_room_id: targetRoomId,
      target_slot: targetSlot,
      day_name: props.date
    })

    if (response.data.success) {
      emit('operation-updated', {
        operationId: operation.id,
        targetRoomId,
        targetSlot
      })
      alert(MSG_UPDATE_SUCCESS)
    }
  } catch (error) {
    const errorMsg = error.response?.data?.message || MSG_UPDATE_ERROR
    alert(`Taşıma Başarısız: ${errorMsg}`)
  } finally {
    draggedOperation.value = null 
  }
}
</script>

<style scoped>
.schedule-container {
  padding: 20px;
  font-family: Arial, sans-serif;
}

.grid-table {
  display: flex;
  border: 1px solid #ddd;
  overflow-x: auto; 
}

.time-column {
  width: 130px;
  flex-shrink: 0;
  background-color: #f8f9fa;
  border-right: 2px solid #ccc;
}

.room-column {
  flex: 1;
  min-width: 180px;
  border-right: 1px solid #eee;
}

.header-cell {
  height: 45px;
  background-color: #2c3e50;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.time-cell {
  height: 60px;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #666;
  box-sizing: border-box;
}

.slot-cell {
  height: 60px;
  border-bottom: 1px solid #eee;
  padding: 2px;
  position: relative;
  box-sizing: border-box;
  transition: background-color 0.2s;
}

.slot-cell.drag-over {
  background-color: #e3f2fd;
  border: 2px dashed #2196f3;
}

.operation-card {
  background-color: #3498db;
  color: white;
  border-radius: 6px;
  padding: 6px;
  height: 100%;
  box-sizing: border-box;
  cursor: grab;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  z-index: 2;
}

.operation-card:active {
  cursor: grabbing;
  opacity: 0.7;
}

.card-header { font-size: 13px; }

.card-body {
  font-size: 11px;
  display: flex;
  flex-direction: column;
  opacity: 0.9;
}
</style>