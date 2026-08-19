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
              <strong>{{ room.name || `OR-${room.id}` }}</strong>
              <span v-if="room.specialty_type" class="room-capacity">{{ room.specialty_type }}</span>
            </td>

            <!-- 30 Dakikalık Slot Hücreleri -->
            <template v-for="slot in timeSlots" :key="slot.time">
              <!-- 1. Eğer bu slotta YENİ BAŞLAYAN bir ameliyat varsa -->
              <td
                v-if="getOpStartingAt(room.id, slot.index)"
                :colspan="getOpStartingAt(room.id, slot.index).duration_slot || 1"
                class="slot-cell occupied"
              >
                <div
                  class="operation-card"
                  :class="getPriorityClass(getOpStartingAt(room.id, slot.index).priority)"
                  @click="onOperationClick(getOpStartingAt(room.id, slot.index))"
                  :title="`${getOpStartingAt(room.id, slot.index).patient_name || 'Hasta'} - Detaylar için tıklayın`"
                >
                  <div class="op-header">
                    <span class="op-title">
                      {{ getOpStartingAt(room.id, slot.index).patient_name || 'Hasta' }} -
                      {{ getOpStartingAt(room.id, slot.index).operation_name || 'Ameliyat' }}
                    </span>
                    <!-- Öncelik Rozeti -->
                    <span
                      v-if="getOpStartingAt(room.id, slot.index).priority"
                      class="priority-badge"
                    >
                      {{ getOpStartingAt(room.id, slot.index).priority }}
                    </span>
                  </div>

                  <div class="op-surgeon" v-if="getOpStartingAt(room.id, slot.index).surgeonDisplay">
                    👨‍⚕️ {{ getOpStartingAt(room.id, slot.index).surgeonDisplay }}
                  </div>
                  <div class="op-anesthesia" v-if="getOpStartingAt(room.id, slot.index).anesthesiaDisplay">
                    💉 {{ getOpStartingAt(room.id, slot.index).anesthesiaDisplay }}
                  </div>
                  <div class="op-duration">
                    ⏱️ {{ (getOpStartingAt(room.id, slot.index).duration_slot || 1) * 30 }} dk
                  </div>
                </div>
              </td>

              <!-- 2. Eğer bu slot bir ameliyatın devamı DEĞİLSE boş td koy -->
              <td
                v-else-if="!isSlotCoveredByPreviousOp(room.id, slot.index)"
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
  operations: { type: Array, default: () => [] },
  surgeons: { type: Array, default: () => [] },
  anesthesiaTeams: { type: Array, default: () => [] }
})

const emit = defineEmits(['select-operation'])

const onOperationClick = (operation) => {
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

// Operasyonları Salon ve Slot Bilgilerine Göre İşleme
const processedOperations = computed(() => {
  if (!props.operations || props.operations.length === 0) return []

  return props.operations
    .filter(op => {
      // Room kontrolü (Obje veya ID)
      const roomId = op.room_id ?? op.required_room ?? (typeof op.room === 'object' ? op.room?.id : op.room)
      const startSlot = op.start_slot ?? op.calculatedStartSlot

      return roomId !== undefined && roomId !== null && startSlot !== undefined && startSlot !== null
    })
    .map((op) => {
      let assignedRoomId = op.room_id ?? op.required_room ?? (typeof op.room === 'object' ? op.room?.id : op.room)
      const startSlot = op.start_slot ?? op.calculatedStartSlot

      // Cerrah İsmi Çözümleme
      let sDisplay = op.surgeon_name || op.doctor_name
      if (!sDisplay && op.surgeon) {
        if (typeof op.surgeon === 'object') sDisplay = op.surgeon.name || op.surgeon.full_name
        else if (props.surgeons && props.surgeons.length > 0) {
          const match = props.surgeons.find(s => String(s.id) === String(op.surgeon))
          if (match) sDisplay = match.name || match.full_name
        }
      }

      // Anestezi İsmi Çözümleme
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

// Tam olarak bu slotta Başlayan ameliyatı getirir
const getOpStartingAt = (roomId, slotIndex) => {
  return processedOperations.value.find(op => {
    return op.calculatedRoomId === String(roomId) && op.calculatedStartSlot === Number(slotIndex)
  })
}

// Bir önceki ameliyatın kapsadığı (colspan ile uzayan) slotları tespit eder
const isSlotCoveredByPreviousOp = (roomId, slotIndex) => {
  return processedOperations.value.some(op => {
    if (op.calculatedRoomId !== String(roomId)) return false
    const start = op.calculatedStartSlot
    const dur = Number(op.duration_slot || 1)

    // Slot başlangıç noktasından SONRAKİ kapsanan aralıktaysa
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
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease-in-out;
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