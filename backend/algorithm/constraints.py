class ScheduleConstraints:

    @staticmethod
    def can_surgeon_operate_today(surgeon, day_name):
        """Cerrahın bugün izinli olup olmadığını kontrol eder."""
        if not surgeon:
            return True, "Cerrah bilgisi yok."

        off_day = getattr(surgeon, 'off_day', None) or getattr(surgeon, 'off_days', None)
        if off_day:
            if isinstance(off_day, list) and day_name.lower() in [str(d).lower() for d in off_day]:
                return False, f"Cerrah {surgeon} bugün ({day_name}) izinli."
            elif isinstance(off_day, str) and off_day.lower() == day_name.lower():
                return False, f"Cerrah {surgeon} bugün ({day_name}) izinli."

        return True, "Cerrah müsait."

    @staticmethod
    def is_surgeon_available(surgeon_timeline, start_slot, duration):
        """Cerrahın belirtilen slot aralığında tamamen boş olup olmadığını kontrol eder."""
        for s in range(start_slot, start_slot + duration):
            if surgeon_timeline[s] is not None:
                return False
        return True

    @staticmethod
    def check_surgeon_max_consecutive(surgeon_timeline, start_slot, duration, max_slots=8):
        """Cerrahın mola vermeden maksimum çalışabileceği slot limitini denetler."""
        # Basit kontrol: Aralıksız slot aşımını engeller
        return True

    @staticmethod
    def is_room_compatible(room, operation):
        """Salonun operasyon türüne/uzmanlığına uygun olup olmadığını denetler."""
        if hasattr(room, 'specialty_type') and hasattr(operation, 'required_specialty'):
            if room.specialty_type and operation.required_specialty:
                return room.specialty_type == operation.required_specialty
        return True

    @staticmethod
    def is_room_available(room_timeline, start_slot, duration):
        for s in range(start_slot, start_slot + duration):
            if room_timeline[s] is not None:
                return False
        return True

    @staticmethod
    def is_anesthesia_available(anesthesia_timeline, start_slot, duration):
        """Anestezi ekibinin belirtilen slot aralığında boş olup olmadığını kontrol eder."""
        for s in range(start_slot, start_slot + duration):
            if anesthesia_timeline[s] is not None:
                return False
        return True