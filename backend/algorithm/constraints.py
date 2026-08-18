from .constants import DEFAULT_TOTAL_SLOTS, SPECIAL_ROOM_MAPPING, DAY_MAPPING


def check_slot_bounds(start_slot, duration_slot, total_slots=DEFAULT_TOTAL_SLOTS):
    return (start_slot + duration_slot) <= total_slots


def is_surgeon_available_on_day(surgeon, day_name):
    off_day = getattr(surgeon, 'off_day', None)
    if not off_day:
        return True

    off_day_clean = str(off_day).strip().lower()
    day_tr_clean = str(day_name).strip().lower()
    day_en_clean = DAY_MAPPING.get(day_name, '').lower()

    return off_day_clean not in (day_tr_clean, day_en_clean)


def is_specialty_matching(surgeon, operation):
    return surgeon.specialty == operation.required_specialty


def is_room_compatible(room, operation):
    required_room_name = SPECIAL_ROOM_MAPPING.get(getattr(operation, 'required_specialty', ''))

    if required_room_name and room.name != required_room_name:
        return False

    if operation.required_room and operation.required_room.id != room.id:
        return False

    return True


def is_resource_free(resource_schedule, resource_id, start_slot, duration_slot):
    slots = resource_schedule.get(resource_id, [])
    for offset in range(duration_slot):
        curr_slot = start_slot + offset

        if curr_slot >= len(slots) or slots[curr_slot] is not None:
            return False

    return True


def can_assign_operation(operation, surgeon, room, anesthesia, start_slot, day_name,
                         room_schedule, surgeon_schedule, anesthesia_schedule,
                         total_slots=DEFAULT_TOTAL_SLOTS):
    if not check_slot_bounds(start_slot, operation.duration_slot, total_slots):
        return False

    if not is_surgeon_available_on_day(surgeon, day_name):
        return False

    if not is_specialty_matching(surgeon, operation):
        return False

    if not is_room_compatible(room, operation):
        return False

    if not is_resource_free(room_schedule, room.id, start_slot, operation.duration_slot):
        return False

    if not is_resource_free(surgeon_schedule, surgeon.id, start_slot, operation.duration_slot):
        return False

    if not is_resource_free(anesthesia_schedule, anesthesia.id, start_slot, operation.duration_slot):
        return False

    return True