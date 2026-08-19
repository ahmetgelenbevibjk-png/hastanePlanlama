from .constants import (
    SPECIAL_ROOM_MAPPING,
    PENALTY_SPECIALTY_MISMATCH,
    PENALTY_ROOM_MISMATCH,
    PENALTY_CRITICAL_DELAY_WEIGHT,
    PENALTY_REST_VIOLATION,
    PENALTY_IDLE_SLOT,
)

# Sabitlerde tanımlı değilse varsayılan gecikme katsayısı
PENALTY_NORMAL_DELAY_WEIGHT = 5


def check_specialty_penalty(surgeon, operation):
    if getattr(surgeon, 'specialty', None) != getattr(operation, 'required_specialty', None):
        return PENALTY_SPECIALTY_MISMATCH
    return 0


def check_room_penalty(room, operation):
    penalty = 0
    required_room_name = SPECIAL_ROOM_MAPPING.get(getattr(operation, 'required_specialty', ''))
    
    # DÜZELTME: Güvenli attribute okuma
    room_name = getattr(room, 'name', None)
    room_id = getattr(room, 'id', room)

    if required_room_name and room_name != required_room_name:
        penalty += PENALTY_ROOM_MISMATCH

    req_room = getattr(operation, 'required_room', None)
    if req_room:
        req_room_id = getattr(req_room, 'id', req_room)
        if req_room_id != room_id:
            penalty += PENALTY_ROOM_MISMATCH

    return penalty


def check_priority_delay_penalty(operation, start_slot):
    priority = str(getattr(operation, 'priority', 'NORMAL')).upper()
    if priority in ['KRITIK', 'ACIL', 'HIGH', 'YÜKSEK']:
        return start_slot * PENALTY_CRITICAL_DELAY_WEIGHT
    elif priority == 'NORMAL':
        return start_slot * PENALTY_NORMAL_DELAY_WEIGHT
    return 0


def check_surgeon_rest_penalty(surgeon_schedule, surgeon_id, start_slot, duration_slot):
    slots = surgeon_schedule.get(surgeon_id, [])
    if not slots:
        return 0

    # 1. Geriye dönük kesintisiz çalışma hesabı
    backward_consecutive = 0
    check_idx = start_slot - 1
    while check_idx >= 0 and slots[check_idx] is not None:
        backward_consecutive += 1
        check_idx -= 1

    # DÜZELTME: 2. İleriye dönük kesintisiz çalışma hesabı (İki blok arasına yerleşme kontrolü)
    forward_consecutive = 0
    check_idx = start_slot + duration_slot
    while check_idx < len(slots) and slots[check_idx] is not None:
        forward_consecutive += 1
        check_idx += 1

    total_consecutive = backward_consecutive + duration_slot + forward_consecutive

    if total_consecutive > 4:
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

    # DÜZELTME: Güvenli id ve duration_slot alımı
    surgeon_id = getattr(surgeon, 'id', surgeon)
    room_id = getattr(room, 'id', room)
    duration_slot = getattr(operation, 'duration_slot', 1)

    total_penalty += check_specialty_penalty(surgeon, operation)
    total_penalty += check_room_penalty(room, operation)
    total_penalty += check_priority_delay_penalty(operation, start_slot)

    if surgeon_schedule:
        total_penalty += check_surgeon_rest_penalty(
            surgeon_schedule, surgeon_id, start_slot, duration_slot
        )

    if room_schedule:
        total_penalty += check_idle_time_penalty(room_schedule, room_id, start_slot)

    return total_penalty