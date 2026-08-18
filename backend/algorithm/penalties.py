from .constants import (SPECIAL_ROOM_MAPPING,
PENALTY_SPECIALTY_MISMATCH,
PENALTY_ROOM_MISMATCH,
PENALTY_CRITICAL_DELAY_WEIGHT,
PENALTY_REST_VIOLATION,
PENALTY_IDLE_SLOT,
                        )


def check_specialty_penalty(surgeon,operation):

    if getattr(surgeon,'specialty',None) !=getattr(operation,'required_specialty',None):
        return PENALTY_SPECIALTY_MISMATCH
    return 0

def check_room_penalty(room,operation):
    penalty=0
    required_room_name=SPECIAL_ROOM_MAPPING.get(getattr(operation,'required_specialty',''))

    if required_room_name and room.name !=required_room_name:
        penalty += PENALTY_ROOM_MISMATCH

    if getattr(operation,'required_room',None) and operation.required_room.id !=room.id:
        penalty += PENALTY_ROOM_MISMATCH
    return penalty

def check_priority_delay_penalty(operation,start_slot):
    priority = str(getattr(operation,'priority','NORMAL')).upper()
    if priority in ['KRITIK','ACIL','HIGH','YÜKSEK']:
        return start_slot * PENALTY_CRITICAL_DELAY_WEIGHT
    elif priority =='NORMAL':
        return start_slot * 5
    return 0

def check_surgeon_rest_penalty(surgeon_schedule, surgeon_id, start_slot, duration_slot):
    slots = surgeon_schedule.get(surgeon_id, [])
    if not slots:
        return 0

    consecutive = 0
    check_idx = start_slot - 1
    while check_idx >= 0 and slots[check_idx] is not None:
        consecutive += 1
        check_idx -= 1

    if consecutive >= 4 or (consecutive + duration_slot > 4):
        return PENALTY_REST_VIOLATION

    return 0

def check_idle_time_penalty(resource_schedule, resource_id, start_slot):
    slots = resource_schedule.get(resource_id, [])
    if not slots or start_slot == 0:
        return 0

    last_occupied = -1
    for i in range(start_slot - 1, -1, -1):
        if slots[i] is not None:
            last_occupied = i
            break

    if last_occupied != -1:
        gap = start_slot - last_occupied - 1
        if gap > 0:
            return gap * PENALTY_IDLE_SLOT

    return 0

def calculate_assignment_penalty(operation, surgeon, room, anesthesia, start_slot,
                                  room_schedule=None, surgeon_schedule=None):
    total_penalty = 0

    total_penalty += check_specialty_penalty(surgeon, operation)

    total_penalty += check_room_penalty(room, operation)

    total_penalty += check_priority_delay_penalty(operation, start_slot)

    if surgeon_schedule:
        total_penalty += check_surgeon_rest_penalty(
            surgeon_schedule, surgeon.id, start_slot, operation.duration_slot
        )

    if room_schedule:
        total_penalty += check_idle_time_penalty(room_schedule, room.id, start_slot)

    return total_penalty