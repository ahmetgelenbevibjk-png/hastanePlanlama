from datetime import datetime
from room.models import OperatingRoom
from surgeon.models import Surgeon
from anesthesia.models import AnesthesiaTeam
from patient_operation.models import PatientOperation
from .constraints import ScheduleConstraints

class ScheduleOptimizer:
    TOTAL_SLOTS =20
    def __init__(self,target_date_str):

        self.target_date_str =target_date_str
        self.date_obj=datetime.strptime(target_date_str, "%Y-%m-%d")
        self.day_name= self.date_obj.strftime("%A").lower()

        self.rooms =[]
        self.surgeons=[]
        self.anesthesia_teams=[]
        self.operations=[]

        self.room_timelines={}
        self.surgeon_timelines={}
        self.anesthesia_timelines={}

    def load_data(self):

        self.rooms=list(OperatingRoom.objects.filter(is_active=True))
        self.surgeons=list(Surgeon.objects.filter(is_active=True))
        self.anesthesia_teams=list(AnesthesiaTeam.objects.filter(is_active=True))



        priority_order={'EMERGENCY':0 ,'CRITICAL':1,'HIGH':2,'MEDIUM':3,'LOW':4}
        all_ops=list(PatientOperation.objects.filter(is_active=True,is_scheduled=False))
        self.operations=sorted(all_ops,key=lambda x:priority_order.get(x.priority,5))

        for room in self.rooms:
            self.room_timelines[room.id]=[None]*self.TOTAL_SLOTS

        for surgeon in self.surgeons:
            self.surgeon_timelines[surgeon.id]=[None]*self.TOTAL_SLOTS

        for team in self.anesthesia_teams:
            self.anesthesia_timelines[team.id]=[None]*self.TOTAL_SLOTS

    def optimiz(self):

        self.load_data()

        scheduled_count=0
        unscheduled_count=0

        for op in self.operations:
            assignment=self._find_best_assignment(op)

            if assignment:
                room_id=assignment['room_id']
                team_id=assignment['team_id']
                start_slot=assignment['start_slot']
                duration=op.duration.slot

                for s in range(start_slot,start_slot+duration):
                    self.room_timelines[room_id][s]= op.id
                    self.surgeon_timelines[op.surgeon.id][s]= op.id
                    self.anesthesia_timelines[team_id][s]=op.id

                op.assigned_room_id=room_id
                op.assigned_team_id=team_id
                op.assigned_start_slot=start_slot
                op.is_scheduled_temp=True

                scheduled_count+=1
            else:
                op.is_scheduled_temp=False
                unscheduled_count+=1

        return {
            'scheduled_count': scheduled_count,
            'uncheduled_count':unscheduled_count,
            'total_operations': len(self.operations)
        }

    def _find_best_assignment(self,op):

        duration=op.duration_slot

        can_surgeon,surgeon_msg= ScheduleConstraints.can_surgeon_operate_today(
            op.surgeon,self.day_name
        )
        if not can_surgeon:
            return None

        for start_slot in range(0, self.TOTAL_SLOTS - duration + 1):

            # 1. Cerrah bu slot aralığında boş mu?
            if not ScheduleConstraints.is_surgeon_available(
                    self.surgeon_timelines[op.surgeon.id], start_slot, duration
            ):
                continue

            if not ScheduleConstraints.check_surgeon_max_consecutive(
                    self.surgeon_timelines[op.surgeon.id], start_slot, duration
            ):
                continue

            for room in self.rooms:
                if not ScheduleConstraints.is_room_compatible(room, op):
                    continue

                if not ScheduleConstraints.is_room_available(
                        self.room_timelines[room.id], start_slot, duration
                ):
                    continue

                for team in self.anesthesia_teams:
                    if not ScheduleConstraints.is_anesthesia_available(
                            self.anesthesia_timelines[team.id], start_slot, duration
                    ):
                        continue

                    return {
                        'room_id':room.id,
                        'team_id':team.id,
                        'start_slot':start_slot
                    }
                
        return None