class HospitalScheduler:
    TOTAL_SLOTS=20

    def __init__(self,operations,rooms,surgeons,anesthesia_teams):
        self.operations=operations
        self.rooms=rooms
        self.surgeons=surgeons
        self.anesthesia_teams=anesthesia_teams

        self.schedule={room.id:[None]*self.TOTAL_SLOTS for room in rooms}
        self.surgeon_schedule={surgeon.id:[None]*self.TOTAL_SLOTS for surgeon in surgeons}
        self.anesthesia_schedule={team.id:[None]*self.TOTAL_SLOTS for team in anesthesia_teams}


    def solve(self):
        priority_map={'CRITICAL':4,'HIGH':3,'MEDIUM':2,'LOW':1}
        sorted_ops=sorted(
            self.operations,
            key=lambda x:priority_map.get(x.priority,0),
            reverse=True
        )

        placed_operations=[]
        unplaced_operations=[]

        for op in sorted_ops:
            is_placed=self._place_operation(op)
            if is_placed:
                placed_operations.append(op)
            else:
                unplaced_operations.append(op)

        return {
            "schedule":self.schedule,
            "placed":placed_operations,
            "unplaced":unplaced_operations
        }

    def _place_operation(self,op):
        duration=op.duration_slot

        for start_slot in range(0,self.TOTAL_SLOTS - duration +1):
            end_slot=start_slot+duration

            for room in self.rooms:

                if op.required_room and op.required_room.id != room.id:
                    continue

                if any(self.schedule[room.id][s]is not None for s in range(start_slot,end_slot)):
                    continue

                suitable_surgeon=self._find_free_surgeon(op.required_specialty,start_slot,end_slot)
                if not suitable_surgeon:
                        continue

                suitable_anesthesia=self._find_free_anesthesia(start_slot,end_slot)
                if not suitable_anesthesia:
                    continue

                for s in range(start_slot,end_slot):
                    self.schedule[room.id][s]=op.id
                    self.surgeon_schedule[suitable_surgeon.id][s]=op.id
                    self.anesthesia_schedule[suitable_anesthesia.id][s]=op.id

                op.assigned_room=room
                op.assigned_surgeon=suitable_surgeon
                op.assigned_anesthesia=suitable_anesthesia
                op.start_slot=start_slot +1
                return True
            return False


    def _find_free_anesthesia(self,start_slot,end_slot):
        for team in self.anesthesia_teams:
            if all(self.anesthesia_schedule[team.id][s]is None for s in range(start_slot,end_slot)):
                return team

        return None
    














