<template>
  <div class="schedule-grid-container">
    <div class="table-wrapper">
      <table class="timeline-table">
        <thead>
          <tr>
            <th class="room-column">Salon / Saat</th>
            <th v-for="time in timeSlots" :key="time" class="time-header">
              {{ time }}
            </th>
          </tr>
        </thead>
        <tbody>
          <!-- Salonlar Listesi -->
          <tr v-for="room in rooms" :key="room.id">
            <td class="room-cell">
              <strong>{{ room.name }}</strong>
              <span v-if="room.type" class="room-capacity">{{ room.type }}</span>
            </td>

            <!-- Saat Dilimleri -->
            <td v-for="time in timeSlots" :key="time" class="slot-cell">
              <div
                v-if="getOperationForSlot(room.id, time)"
                class="operation-card"
                :class="getOperationForSlot(room.id, time).status || 'planned'"
              >
                <div class="op-title">{{ getOperationForSlot(room.id, time).name }}</div>
                <div class="op-surgeon">👨‍⚕️ {{ getOperationForSlot(room.id, time).surgeon }}</div>
              </div>
            </td>
          </tr>

          <!-- Eğer hiç salon/veri eklenmediyse -->
          <tr v-if="rooms.length === 0">
            <td :colspan="timeSlots.length + 1" class="no-data">
              Henüz tanımlanmış bir ameliyathane salonu bulunmuyor. "Salonlar" sekmesinden yeni salon ekleyebilirsiniz.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  date: {
    type: String,
    required: true
  },
  // Dışarıdan veya API'den gelecek olan gerçek veriler
  rooms: {
    type: Array,
    default: () => []
  },
  operations: {
    type: Array,
    default: () => []
  }
})

// Saat Dilimleri (08:00 - 16:00)
const timeSlots = ref([
  '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00','17:00','18:00'
])

const getOperationForSlot = (roomId, time) => {
  return props.operations.find(op => op.roomId === roomId && op.time === time)
}
</script>

<style scoped>
.schedule-grid-container {
  width: 100%;
  overflow-x: auto;
}

.table-wrapper {
  min-width: 900px;
}

.timeline-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.timeline-table th, .timeline-table td {
  border: 1px solid #e2e8f0;
  padding: 10px;
  text-align: center;
}

.room-column {
  width: 180px;
  background-color: #f8fafc;
  font-weight: 600;
  color: #334155;
  text-align: left !important;
  padding-left: 16px !important;
}

.time-header {
  background-color: #f1f5f9;
  color: #475569;
  font-size: 0.85rem;
  font-weight: 600;
  width: 100px;
}

.room-cell {
  text-align: left !important;
  padding-left: 16px !important;
  background-color: #f8fafc;
}

.room-capacity {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  font-weight: normal;
}

.slot-cell {
  height: 70px;
  vertical-align: middle;
  padding: 4px !important;
  background-color: #ffffff;
}

.operation-card {
  padding: 6px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  text-align: left;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.op-title {
  font-weight: 700;
}

.op-surgeon {
  font-size: 0.7rem;
  opacity: 0.9;
}

.operation-card.planned {
  background-color: #e0f2fe;
  color: #0369a1;
  border-left: 3px solid #0284c7;
}

.no-data {
  padding: 30px;
  color: #64748b;
  font-size: 0.9rem;
}
</style>