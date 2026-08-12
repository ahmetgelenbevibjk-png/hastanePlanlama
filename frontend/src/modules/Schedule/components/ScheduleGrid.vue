<template>
  <div class="schedule-grid-container">
    <div class="table-wrapper">
      <table class="timeline-table">
        <thead>
          <tr>
            <th class="room-column">Salon / Slot</th>
            <th v-for="slot in timeSlots" :key="slot.time" class="time-header">
              {{ slot.time }}
            </th>
          </tr>
        </thead>
        <tbody>
          <!-- Salonlar Listesi -->
          <tr v-for="(room, rIndex) in rooms" :key="room.id">
            <td class="room-cell">
              <strong>{{ room.name }}</strong>
              <span v-if="room.specialty_type" class="room-capacity">{{ room.specialty_type }}</span>
            </td>

            <!-- 30 Dakikalık Slot Hücreleri -->
            <template v-for="(slot, sIndex) in timeSlots" :key="slot.time">
              <!-- Eğer bu slotta yeni başlayan bir ameliyat varsa render et -->
              <td
                v-if="getOpStartingAt(room.id, rIndex, sIndex)"
                :colspan="getOpStartingAt(room.id, rIndex, sIndex).duration_slot || 1"
                class="slot-cell occupied"
              >
                <div
                  class="operation-card planned"
                  @click="onOperationClick(getOpStartingAt(room.id, rIndex, sIndex))"
                  :title="`${getOpStartingAt(room.id, rIndex, sIndex).patient_name || 'Hasta'} - Detaylar için tıklayın`"
                >
                  <div class="op-title">
                    {{ getOpStartingAt(room.id, rIndex, sIndex).patient_name || 'Hasta' }} -
                    {{ getOpStartingAt(room.id, rIndex, sIndex).operation_name || 'Ameliyat' }}
                  </div>
                  <div class="op-surgeon" v-if="getOpStartingAt(room.id, rIndex, sIndex).surgeon">
                    👨‍⚕️ {{ getOpStartingAt(room.id, rIndex, sIndex).surgeon }}
                  </div>
                  <div class="op-anesthesia" v-if="getOpStartingAt(room.id, rIndex, sIndex).anesthesia">
                    💉 {{ getOpStartingAt(room.id, rIndex, sIndex).anesthesia }}
                  </div>
                  <div class="op-duration">
                    ⏱️ {{ (getOpStartingAt(room.id, rIndex, sIndex).duration_slot || 1) * 30 }} dk
                  </div>
                </div>
              </td>

              <!-- Eğer bu slot başka bir ameliyatın devamı değilse boş td koy -->
              <td
                v-else-if="!isSlotCovered(room.id, rIndex, sIndex)"
                class="slot-cell empty"
              ></td>
            </template>
          </tr>

          <!-- Eğer hiç salon yoksa -->
          <tr v-if="rooms.length === 0">
            <td :colspan="timeSlots.length + 1" class="no-data">
              Henüz tanımlanmış bir ameliyathane salonu bulunmuyor.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  date: { type: String, required: true },
  rooms: { type: Array, default: () => [] },
  operations: { type: Array, default: () => [] }
})

// Tıklama olayını üst bileşene (ScheduleView) fırlatmak için emit
const emit = defineEmits(['select-operation'])

const onOperationClick = (operation) => {
  console.log('Tıklanan Operasyon:', operation)
  emit('select-operation', operation)
}

// 08:00 - 18:00 arası 20 Slot
const timeSlots = [
  { index: 0, time: '08:00' }, { index: 1, time: '08:30' },
  { index: 2, time: '09:00' }, { index: 3, time: '09:30' },
  { index: 4, time: '10:00' }, { index: 5, time: '10:30' },
  { index: 6, time: '11:00' }, { index: 7, time: '11:30' },
  { index: 8, time: '12:00' }, { index: 9, time: '12:30' },
  { index: 10, time: '13:00' }, { index: 11, time: '13:30' },
  { index: 12, time: '14:00' }, { index: 13, time: '14:30' },
  { index: 14, time: '15:00' }, { index: 15, time: '15:30' },
  { index: 16, time: '16:00' }, { index: 17, time: '16:30' },
  { index: 18, time: '17:00' }, { index: 19, time: '17:30' }
]

const processedOperations = computed(() => {
  if (!props.operations || props.operations.length === 0) return []
  if (!props.rooms || props.rooms.length === 0) return []

  return props.operations.map((op, index) => {
    let assignedRoomId = op.required_room || op.room_id || op.room
    if (!assignedRoomId || assignedRoomId === null) {
      const fallbackRoomIndex = index % props.rooms.length
      assignedRoomId = props.rooms[fallbackRoomIndex]?.id
    }

    let startSlot = op.start_slot ?? op.slot_index
    if (startSlot === undefined || startSlot === null) {
      startSlot = (Math.floor(index / props.rooms.length) * 2) % 18
    }

    return {
      ...op,
      calculatedRoomId: assignedRoomId,
      calculatedStartSlot: Number(startSlot)
    }
  })
})

const getOpStartingAt = (roomId, roomIndex, slotIndex) => {
  return processedOperations.value.find(op => {
    return String(op.calculatedRoomId) === String(roomId) && Number(op.calculatedStartSlot) === Number(slotIndex)
  })
}

const isSlotCovered = (roomId, roomIndex, slotIndex) => {
  return processedOperations.value.some(op => {
    if (String(op.calculatedRoomId) !== String(roomId)) return false
    const start = Number(op.calculatedStartSlot)
    const dur = Number(op.duration_slot || 1)
    return slotIndex >= start && slotIndex < (start + dur)
  })
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
}
.slot-cell.empty { background-color: #fafafa; }


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
  cursor: pointer; /* Tıklanabilir imleç */
  user-select: none;
  transition: all 0.2s ease-in-out; /* Akıcı animasyon */
}

.operation-card.planned {
  background-color: #e0f2fe;
  border-left: 4px solid #0284c7;
}

/* HOVER DURUMU */
.operation-card:hover {
  transform: translateY(-2px); /* Hafif yukarı kalkma */
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25); /* Mavi parıltılı gölge */
  background-color: #bae6fd; /* Bir tık daha koyu açık mavi */
  border-left-color: #0369a1;
}

/* AKTİF (TIKLANMA) DURUMU */
.operation-card:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(2, 132, 199, 0.2);
}

.op-title {
  font-weight: 700;
  color: #0369a1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.op-surgeon, .op-anesthesia, .op-duration {
  font-size: 0.68rem;
  color: #334155;
  white-space: nowrap;
}

.no-data { padding: 30px; color: #64748b; font-size: 0.9rem; }
</style>