class ScheduleConstraints:

    @staticmethod
    def is_surgeon_available_on_day(surgeon,day_code):
        if not surgeon or not surgeon.off_day:
            return True
        return surgeon.off_day.lower() !=day_code.lower()

    @staticmethod
    def is_specialty_matching(surgeon,operation):
        if not operation.required_specialty:
            return True
        if not surgeon or not surgeon.specialty:
            return False
        return surgeon.specialty.strip().lower() == operation.required_specialty.strip().lower()

    @staticmethod
    def is_room_compatible(room,operation):
        if operation.required_room_id:
            return room.id == operation.required_room_id
        if room.specialty_type and operation.required_specialty:
            return room.specialty_type.strip().lower() == operation.required_specialty.strip().lower()

        return True
    @staticmethod
    def is_timeline_slot_free(timeline,start_slot,duration_slot):
        total_slots=len(timeline)

        if start_slot + duration_slot >total_slots:
            return False

        for slot in range(start_slot, start_slot + duration_slot):
            if timeline[slot] is not None:
                return False

        return True

    @staticmethod
    def check_surgeon_rest_rule(surgeon_timeline,start_slot,duration_slot):

        total_slots=len(surgeon_timeline)

        temp_timeline=list(surgeon_timeline)
        for s in range(start_slot,start_slot+duration_slot):
            temp_timeline[s]=True

        consecutive_work= 0
        for slot_val in temp_timeline:
            if slot_val is not None:
                consecutive_work+=1
                if consecutive_work>4:
                    return False
            else:
                consecutive_work=0

        return True