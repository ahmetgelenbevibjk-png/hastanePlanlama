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


def _is_slot_occupied(slots, slot_idx):
    """Hem Optimizer (matris) hem Views (indeks listesi) formatındaki doluluk kontrolünü güvenli yapar."""
    if not slots or slot_idx < 0:
        return False
    # Views formatı: Liste slot indekslerinden oluşuyorsa (Örn: [0, 1, 4, 5])
    if isinstance(slots[0], int) and not isinstance(slots[0], bool):
        return slot_idx in slots
    # Optimizer formatı: Sabit uzunluklu matris (Örn: [None, 'op_1', None])
    if slot_idx < len(slots):
        return slots[slot_idx] is not None and slots[slot_idx] is not False
    return False


def check_specialty_penalty(surgeon, operation):
    req_spec = getattr(operation, 'required_specialty', None)
    if not req_spec:  # Ameliyat özel uzmanlık istemiyorsa ceza kesme
        return 0
    
    surgeon_spec = getattr(surgeon, 'specialty', None)
    if surgeon_spec != req_spec:
        return PENALTY_SPECIALTY_MISMATCH
    return 0


def check_room_penalty(room, operation):
    penalty = 0
    req_spec = getattr(operation, 'required_specialty', '') or ''
    required_room_name = SPECIAL_ROOM_MAPPING.get(req_spec)
    
    room_name = getattr(room, 'name', None)
    room_id = getattr(room, 'id', room)

    if required_room_name and room_name and room_name != required_room_name:
        penalty += PENALTY_ROOM_MISMATCH

    req_room = getattr(operation, 'required_room', None)
    if req_room:
        req_room_id = getattr(req_room, 'id', req_room)
        if room_id is not None and req_room_id != req_room_id:
            penalty += PENALTY_ROOM_MISMATCH

    return penalty


def check_priority_delay_penalty(operation, start_slot):
    priority = str(getattr(operation, 'priority', 'NORMAL')).upper().strip()
    critical_keywords = ('KRITIK', 'KRİTİK', 'ACIL', 'ACİL', 'HIGH', 'YÜKSEK', 'YUKSEK', 'URGENT')
    
    if any(kw in priority for kw in critical_keywords):
        return start_slot * PENALTY_CRITICAL_DELAY_WEIGHT
    elif 'NORMAL' in priority:
        return start_slot * PENALTY_NORMAL_DELAY_WEIGHT
    return 0


def check_surgeon_rest_penalty(surgeon_schedule, surgeon_id, start_slot, duration_slot):
    slots = surgeon_schedule.get(surgeon_id, [])
    if not slots:
        return 0

    # 1. Geriye dönük kesintisiz çalışma hesabı
    backward_consecutive = 0
    check_idx = start_slot - 1
    while check_idx >= 0 and _is_slot_occupied(slots, check_idx):
        backward_consecutive += 1
        check_idx -= 1

    # 2. İleriye dönük kesintisiz çalışma hesabı
    forward_consecutive = 0
    check_idx = start_slot + duration_slot
    
    # Döngü için üst sınır güvenliği
    max_search_limit = start_slot + duration_slot + 10
    while check_idx <= max_search_limit and _is_slot_occupied(slots, check_idx):
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
        if _is_slot_occupied(slots, i):
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

    surgeon_id = getattr(surgeon, 'id', surgeon)
    room_id = getattr(room, 'id', room)
    duration_slot = getattr(operation, 'duration_slot', 1)

    total_penalty += check_specialty_penalty(surgeon, operation)
    total_penalty += check_room_penalty(room, operation)
    total_penalty += check_priority_delay_penalty(operation, start_slot)

    if surgeon_schedule and surgeon_id is not None:
        total_penalty += check_surgeon_rest_penalty(
            surgeon_schedule, surgeon_id, start_slot, duration_slot
        )

    if room_schedule and room_id is not None:
        total_penalty += check_idle_time_penalty(room_schedule, room_id, start_slot)

    return total_penalty