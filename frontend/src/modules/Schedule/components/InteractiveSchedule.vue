<template>
  <div class="schedule-container">
    <h2>Ameliyat Planlama Çizelgesi (Sürükle - Bırak)</h2>

    <div class="grid-table">
      <!-- Sol Sütun: Saat Slotları -->
      <div class="time-column">
        <div class="header-cell">Saat / Slot</div>
        <div 
          v-for="slot in totalSlots" 
          :key="slot - 1" 
          class="time-cell"
        >
          Slot {{ slot - 1 }} ({{ getSlotTime(slot - 1) }})
        </div>
      </div>

      <!-- Ameliyathane Sütunları -->
      <div 
        v-for="room in rooms" 
        :key="room.id" 
        class="room-column"
      >
        <!-- Salon Başlığı -->
        <div class="header-cell room-header">
          {{ room.name }}
        </div>

        <!-- Slot Hücreleri (Sürüklenen Kartların Bırakılacağı Alanlar) -->
        <div 
          v-for="slotIdx in totalSlots" 
          :key="slotIdx - 1" 
          class="slot-cell"
          :class="{ 'drag-over': isDragOver(room.id, slotIdx - 1) }"
          @dragover.prevent="handleDragOver(room.id, slotIdx - 1)"
          @dragleave="handleDragLeave"
          @drop="handleDrop($event, room.id, slotIdx - 1)"
        >
          <!-- Eğer bu slotta ameliyat varsa kartı çiz -->
          <div 
            v-if="getOperationAt(room.id, slotIdx - 1)"
            class="operation-card"
            draggable="true"
            @dragstart="handleDragStart($event, getOperationAt(room.id, slotIdx - 1), room.id, slotIdx - 1)"
          >
            <div class="card-header">
              <strong>{{ getOperationAt(room.id, slotIdx - 1).operation_name }}</strong>
            </div>
            <div class="card-body">
              <span>Cerrah: {{ getOperationAt(room.id, slotIdx - 1).surgeon_name }}</span>
              <span>Süre: {{ getOperationAt(room.id, slotIdx - 1).duration_slot }} Slot</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const totalSlots = ref(20)
const rooms = ref([
  { id: 'OR-1', name: 'OR-1 (Genel Cerrahi)' },
  { id: 'OR-2', name: 'OR-2 (Kardiyoloji)' },
  { id: 'OR-3', name: 'OR-3 (Ortopedi)' },
  { id: 'OR-4', name: 'OR-4 (Beyin Cerrahisi)' }
])

const draggedData = ref(null)
const activeHoverCell = ref(null)

const scheduleData = ref([
  {
    id: 101, // 'is' hatası 'id' olarak düzeltildi
    operation_name: 'Apendektomi',
    surgeon_name: 'Dr. Ahmet',
    duration_slot: 2,
    room_id: 'OR-1',
    start_slot: 2
  }
])

const getSlotTime = (slotIdx) => {
  const startHour = 8 // Yazım hatası düzeltildi
  const totalMinutes = slotIdx * 30 
  const hour = Math.floor(startHour + totalMinutes / 60)
  const minutes = totalMinutes % 60 === 0 ? '00' : '30'
  return `${hour.toString().padStart(2, '0')}:${minutes}`
}

const getOperationAt = (roomId, slotIdx) => {
  return scheduleData.value.find(
    op => op.room_id === roomId && op.start_slot === slotIdx 
  )
}

const handleDragStart = (event, operation, currentRoomId, currentSlot) => {
  draggedData.value = {
    operation,
    fromRoomId: currentRoomId,
    fromSlot: currentSlot 
  }
  event.dataTransfer.setData('text/plain', JSON.stringify(operation))
  event.dataTransfer.effectAllowed = 'move'
}

const handleDragOver = (roomId, slotIdx) => {
  activeHoverCell.value = `${roomId}-${slotIdx}` // Backtick eklendi
}

const handleDragLeave = () => {
  activeHoverCell.value = null // Hover sıfırlama düzeltildi
}

const isDragOver = (roomId, slotIdx) => {
  return activeHoverCell.value === `${roomId}-${slotIdx}` // Backtick eklendi
}

const handleDrop = async (event, targetRoomId, targetSlot) => {
  activeHoverCell.value = null 
  if (!draggedData.value) return

  const { operation, fromRoomId, fromSlot } = draggedData.value 

  if (fromRoomId === targetRoomId && fromSlot === targetSlot) return 

  try {
    // URL Django endpoint'i ile eşitlendi
    const response = await axios.post('http://localhost:8000/api/algorithm/manual-update/', {
      operation_id: operation.id,
      target_room_id: targetRoomId,
      target_slot: targetSlot,
      day_name: 'Pazartesi'
    })

    if (response.data.success) {
      operation.room_id = targetRoomId 
      operation.start_slot = targetSlot 
      alert('Ameliyat yeri başarıyla güncellendi.')
    }
  } catch (error) {
    const errorMsg = error.response?.data?.message || 'Bu konuma taşıma yapılamaz!'
    alert(`Taşıma Başarısız: ${errorMsg}`) // Backtick eklendi
  } finally {
    draggedData.value = null 
  }
}
</script>

<style scoped>
.schedule-container {
    padding: 20px;
    font-family:Arial,sans-serif;
}

.grid-table {
    display:flex;
    border:1px solid #ddd;
    overflow-x: auto ; 
}

.time-column {
    width:130px;
    flex-shrink: 0 ;
    background-color: #f8f9fa;
    border-right:20px solid #ccc;
}

.room-column {
    flex: 1;
    min-width:180px;
    border-right:1px solid #eee;
}


.header-cell {
    height: 45px;
    background-color: #2c3e50;
    color:white;
    display: flex;
    align-items:center;
    justify-content: center;
    font-weight:bold;
}

.time-cell {
    height:60px;
    border-bottom:1px solid #eee;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:12px;
    color: #666;
}

.slot-cell {
    height:60px;
    border-bottom:1px solid #eee;
    padding:2px;
    position:relative;
    transition:background-color 0.2s;
}

.slot-cell.drag-over {
    background-color: #e3f2fd;
    border:2px dashed #2196f3;
}

.operation-card {
    background-color:#3498db;
    color:white;
    border-radius:6px;
    padding: 6px;
    height:100%;
    cursor:grab;
    box-shadow:0 2px 4px rgba(0,0,0,0.1);
    display:flex;
    flex-direction:column;
    justify-content:space-between;
}


.operation-card:active {
    cursor:grabbing;
    opacity:0.7;
}

.card-header {font-size:13px;}

.card-body {
    font-size:11px;
    display: flex;
    flex-direction:column;
    opacity:0.9;
}


</style>