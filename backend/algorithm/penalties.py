def calculate_fitness_percentage(penalty, max_tolerable_penalty=100):
    if penalty >= max_tolerable_penalty:
        return 0

    percentage = 100 - ((penalty / max_tolerable_penalty) * 100)
    return round(percentage)



def calculate_assignment_penalty(operation, start_slot, surgeon, surgeon_schedule):
    total_penalty=0

    total_penalty += check_critical_wait_time(operation, start_slot)
    total_penalty += check_surgeon_rest(surgeon, start_slot, surgeon_schedule)
    total_penalty += check_surgeon_idle_time(surgeon, start_slot, surgeon_schedule)

    return total_penalty

def check_critical_wait_time(operation,start_slot):
    penalty=0
    priority=str(getattr(operation,'priority','')).upper()

    if priority in ['CRITICAL','KRITIK'] and start_slot>3:
        penalty+=(start_slot - 3) * 15
    elif priority in ['HIGH','YÜKSEK'] and start_slot>7:
        penalty+=(start_slot-7)*8

    return penalty

def check_surgeon_rest(surgeon,start_slot,surgeon_schedule):
    penalty=0
    surgeon_id=getattr(surgeon,'id',surgeon)
    slots=surgeon_schedule.get(surgeon_id,[])

    if start_slot>=4:
        recent_4_slots=slots[start_slot-4:start_slot]

        if all(slot_val is not None for slot_val in recent_4_slots):
            penalty +=40
    return penalty

def check_surgeon_idle_time(surgeon,start_slot,surgeon_schedule):
    penalty=0
    surgeon_id=getattr(surgeon,'id',surgeon)
    slots=surgeon_schedule.get(surgeon_id,[])

    if start_slot>0:
        idle_slots=0
        for i in range(start_slot - 1, - -1):
            if slots[i] is None:
                idle_slots+= 1
            else:
                break

        if idle_slots >1:
            penalty += idle_slots * 5
    return penalty 