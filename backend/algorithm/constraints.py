def check_slot_bounds(start_slot,duration_slot,total_slots=20):
    return(start_slot+duration_slot)<=total_slots

def is_surgeon_available_on_day(surgeon,day_name):

    if not surgeon.off_day:
        return True
    return surgeon.off_day.strip().lower() !=day_name.strip().lower()

SPECIAL_ROOM_MAPPING= {
    'Kalp Anjiyo':'OR-2',
    'Tümör Operasyonu':'OR-4',
    'Omurga Operasyonu':'OR-3'
                      }

def is_specialty_matching(surgeon,operation):
    return surgeon.specialty==operation.required_specialty

def is_room_compatible(room,operation):
    required_room_name=SPECIAL_ROOM_MAPPING.get(operation.operation_name)

    if required_room_name and room.name != required_room_name:
        return False

    if operation.required_room and operation.required_room.id != room.id:
        return False

    return True

def is_resource_free(resource_schedule,resource_id,start_slot,duration_slot):

    slots=resource_schedule.get(resource_id,[])
    for offset in range(duration_slot):
        curr_slot=start_slot+offset

        if curr_slot >=len(slots)or slots[curr_slot] is not None:
            return False

    return True

def has_surgeon_rested(surgeon_schedule,surgeon_id,start_slot):

    slots=surgeon_schedule.get(surgeon_id,[])

    if start_slot<4:
        return True

    recent_4_slots=slots[start_slot-4:start_slot]
    if all(slot_val is not None for slot_val in recent_4_slots):
        return False

    return True

def can_assign_operation(operation,surgeon,room,anesthesia,start_slot,day_name,
                         room_schedule,surgeon_schedule,anesthesia_schedule,total_slots=20):

    if not check_slot_bounds(start_slot,operation.duration_slot,total_slots):
        return False

    if not is_surgeon_available_on_day(surgeon,day_name):
        return False

    if not is_specialty_matching(surgeon,operation):
        return False

    if not is_room_compatible(room,operation):
        return False

    if not has_surgeon_rested(surgeon_schedule,surgeon.id,start_slot):
        return False

    if not is_resource_free(room_schedule, room.id, start_slot, operation.duration_slot):
        return False

    if not is_resource_free(surgeon_schedule, surgeon.id, start_slot, operation.duration_slot):
        return False

    if not is_resource_free(anesthesia_schedule, anesthesia.id, start_slot, operation.duration_slot):
        return False

    return True