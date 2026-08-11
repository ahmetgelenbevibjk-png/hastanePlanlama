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
          <tr v-for="room in rooms" :key="room.id">
            <td class="room-cell">
              <strong>{{ room.name }}</strong>
              <span v-if="room.specialty_type" class="room-capacity">{{ room.specialty_type }}</span>
            </td>

            <!-- 30 Dakikalık Slot Hücreleri -->
            <template v-for="(slot, index) in timeSlots" :key="slot.time">
              <!-- Eğer bu slotta yeni başlayan bir ameliyat varsa render et -->
              <td
                v-if="getOperationStartingAtSlot(room.id, index)"
                :colspan="getOperationStartingAtSlot(room.id, index).duration_slot || 1"
                class="slot-cell occupied"
              >
                <div class="operation-card planned">
                  <div class="op-title">
                    {{ getOperationStartingAtSlot(room.id, index).patient_name }} -
                    {{ getOperationStartingAtSlot(room.id, index).operation_name }}
                  </div>
                  <div class="op-surgeon" v-if="getOperationStartingAtSlot(room.id, index).surgeon_name">
                    👨‍⚕️ {{ getOperationStartingAtSlot(room.id, index).surgeon_name }}
                  </div>
                  <div class="op-anesthesia" v-if="getOperationStartingAtSlot(room.id, index).anesthesia_name">
                    💉 {{ getOperationStartingAtSlot(room.id, index).anesthesia_name }}
                  </div>
                  <div class="op-duration">
                    ⏱️ {{ (getOperationStartingAtSlot(room.id, index).duration_slot || 1) * 30 }} dk
                  </div>
                </div>
              </td>

              <!-- Eğer bu slot başka bir ameliyatın devamı (colspan içinde) değilse boş td koy -->
              <td
                v-else-if="!isSlotCoveredByOperation(room.id, index)"
                class="slot-cell empty"
              ></td>
            </template>
          </tr>

          <!-- Eğer hiç salon/veri eklenmediyse -->
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
  date: {
    type: String,
    required: true
  },
  rooms: {
    type: Array,
    default: () => []
  },
  operations: {
    type: Array,
    default: () => []
  }
})

// 08:00 - 18:00 arası 30'ar dakikalık 20 Slot
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

// İlgili salonda ve bu slot indeksinde TAM BAŞLAYAN operasyonu bulur
const getOperationStartingAtSlot = (roomId, slotIndex) => {
  return props.operations.find(
    op => (op.required_room === roomId || op.room_id === roomId || op.roomId === roomId) &&
          (op.start_slot === slotIndex || op.slot_index === slotIndex)
  )
}

// İlgili slotun önceden başlamış bir operasyon tarafından kaplanıp kaplanmadığını kontrol eder
const isSlotCoveredByOperation = (roomId, slotIndex) => {
  return props.operations.some(op => {
    const rId = op.required_room || op.room_id || op.roomId
    const startSlot = op.start_slot ?? op.slot_index
    const duration = op.duration_slot || 1

    if (rId !== roomId || startSlot === undefined) return false

    // Slot, başlangıç slotu ile (başlangıç + duration - 1) arasında mı?
    return slotIndex >= startSlot && slotIndex < (startSlot + duration)
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

.slot-cell.empty {
  background-color: #fafafa;
}

.operation-card {
  padding: 6px 8px;
  border-radius: 6px;
  font-size: 0.72rem;
  text-align: left;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  gap: 3px;
  height: 100%;
  justify-content: center;
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

.operation-card.planned {
  background-color: #e0f2fe;
  border-left: 4px solid #0284c7;
}

.no-data {
  padding: 30px;
  color: #64748b;
  font-size: 0.9rem;
}
</style>  