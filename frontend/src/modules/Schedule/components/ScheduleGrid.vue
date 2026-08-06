<script setup>
import {TIME_SLOTS} from '@/config/constants';

const props=defineProps({
  rooms:{type:Array,required:true},
  operations:{type:Array,required:true},
});

const timeSlots=TIME_SLOTS;

const getOperationsForCell=(rromId,slotId)=>{
  return props.operations.filter(
      op=>op.required_room===roomId&& op.start_slot===slotId
  );
};

</script>

<template>
<div class="grid-wrapper" v-if="rooms.length>0">
  <table class="schedule-table">
    <thead>
    <tr>
      <th class="sticky-col">Saat / Oda </th>
      <th v-for="room in rooms" :key="room.id">
        {{room.name}}<br />
        <small>{{room.specialty}}</small>
      </th>
    </tr>
    </thead>
    <tbody>
    <tr v-for="slot in timeSlots" :key="slot.id">
      <td class="time-col">{{slot.time}}</td>
      <td v-for="room in rooms" :key="room.id" class="slot-cell">
        <div
          v-for="op in getOperationsForCell(room.id,slot.id)"
          :key="op.id"
          class="operation-card"
          :class="op.priority?.toLowerCase()"
          >
          <strong>{{ op.patient_name }}</strong>
              <span>{{ op.operation_name }}</span>
        </div>
      </td>
    </tr>
    </tbody>
  </table>
</div>

</template>

<style scoped>
.grid-wrapper{
  overflow-x:auto;
}
.schedule-table {width:100%;
border-collapse:collapse;
background:white;
}
.schedule-table th, .schedule-table td {
  border:1px solid #e2e8f0;
  padding:8px;
  text-align:center;
}
.time-col{
  font-weight: bold;
  background-color:#f1f5f9;
  width:120px;
}
.slot-cell {
  height:60px;
  vertical-align:top;
  width:180px;
}
.operation-card {
  background-color: #e0f2fe;
  border-left: 4px solid #0284c7;
  padding: 6px;
  border-radius: 4px;
  text-align: left;
  font-size: 0.85rem; }
.operation-card.critical {
  background-color: #fee2e2;
  border-left-color: #ef4444; }



</style>