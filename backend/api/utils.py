def slot_to_time_string(start_slot:int,duration_slot:int=1)-> str:
    if not start_slot or start_slot<1 or start_slot>20:
        return "Belirsiz Saat"

    base_minutes=8*60

    start_minutes=base_minutes+(start_slot-1)*30
    end_minutes=start_minutes + (duration_slot*30)

    start_hh=start_minutes//60
    start_mm=start_minutes%60

    end_hh=end_minutes//60
    end_mm=end_minutes%60

    return f"{start_hh:02d}:{start_mm:02d}-{end_hh:02d}:{end_mm:02d}"