from datetime import datetime
from room.models import OperatingRoom
from surgeon.models import Surgeon
from anesthesia.models import AnesthesiaTeam
from patient_operation.models import PatientOperation
from .constraints import ScheduleConstraints
from django.db import transaction


class ScheduleOptimizer:
    TOTAL_SLOTS = 20

    def __init__(self, target_date_str):
        self.target_date_str = target_date_str
        self.date_obj = datetime.strptime(target_date_str, "%Y-%m-%d")
        self.day_name = self.date_obj.strftime("%A").lower()

        self.rooms = []
        self.surgeons = []
        self.anesthesia_teams = []
        self.operations = []

        self.room_timelines = {}
        self.surgeon_timelines = {}
        self.anesthesia_timelines = {}

    def load_data(self):
        self.rooms = list(OperatingRoom.objects.filter(is_active=True))
        self.surgeons = list(Surgeon.objects.filter(is_active=True))
        self.anesthesia_teams = list(AnesthesiaTeam.objects.filter(is_active=True))

        priority_order = {'EMERGENCY': 0, 'CRITICAL': 1, 'HIGH': 2, 'MEDIUM': 3, 'LOW': 4}
        all_ops = list(PatientOperation.objects.filter(is_active=True, is_scheduled=False))
        self.operations = sorted(all_ops, key=lambda x: priority_order.get(x.priority, 5))

        for room in self.rooms:
            self.room_timelines[room.id] = [None] * self.TOTAL_SLOTS

        for surgeon in self.surgeons:
            self.surgeon_timelines[surgeon.id] = [None] * self.TOTAL_SLOTS

        for team in self.anesthesia_teams:
            self.anesthesia_timelines[team.id] = [None] * self.TOTAL_SLOTS

    def optimize(self):
        self.load_data()

        scheduled_count = 0
        unscheduled_count = 0

        for op in self.operations:
            assignment = self._find_best_assignment(op)

            if assignment:
                room_id = assignment['room_id']
                surgeon_id = assignment['surgeon_id']
                team_id = assignment['team_id']
                start_slot = assignment['start_slot']
                duration = getattr(op, 'duration_slot', None) or getattr(op, 'duration', 2)

                # Bütün matrisleri seçilen kaynaklara göre dolduruyoruz
                for s in range(start_slot, start_slot + duration):
                    self.room_timelines[room_id][s] = op.id
                    if surgeon_id:
                        self.surgeon_timelines[surgeon_id][s] = op.id
                    if team_id:
                        self.anesthesia_timelines[team_id][s] = op.id

                op.assigned_room_id = room_id
                op.assigned_surgeon_id = surgeon_id
                op.assigned_team_id = team_id
                op.assigned_start_slot = start_slot
                op.is_scheduled_temp = True

                scheduled_count += 1
            else:
                op.is_scheduled_temp = False
                unscheduled_count += 1

        return {
            'scheduled_count': scheduled_count,
            'unscheduled_count': unscheduled_count,
            'total_operations': len(self.operations)
        }

    def _find_best_assignment(self, op):
        duration = getattr(op, 'duration_slot', None) or getattr(op, 'duration', 2)
        op_surgeon = getattr(op, 'surgeon', None)
        op_team = getattr(op, 'anesthesia_team', None) or getattr(op, 'anesthesia', None) or getattr(op, 'team', None)

        for start_slot in range(0, self.TOTAL_SLOTS - duration + 1):
            for room in self.rooms:
                # 1. Salon Uygunluk ve Müsaitlik Kontrolü
                if not ScheduleConstraints.is_room_compatible(room, op):
                    continue

                if not ScheduleConstraints.is_room_available(
                        self.room_timelines[room.id], start_slot, duration
                ):
                    continue

                # 2. Cerrah Seçimi: Atanmış cerrah varsa kontrol et, yoksa havuzdan müsait olanı bul
                assigned_surgeon_id = None
                if op_surgeon:
                    can_surgeon, _ = ScheduleConstraints.can_surgeon_operate_today(op_surgeon, self.day_name)
                    if can_surgeon and ScheduleConstraints.is_surgeon_available(
                            self.surgeon_timelines[op_surgeon.id], start_slot, duration
                    ) and ScheduleConstraints.check_surgeon_max_consecutive(
                        self.surgeon_timelines[op_surgeon.id], start_slot, duration
                    ):
                        assigned_surgeon_id = op_surgeon.id
                else:
                    for surgeon in self.surgeons:
                        can_surgeon, _ = ScheduleConstraints.can_surgeon_operate_today(surgeon, self.day_name)
                        if not can_surgeon:
                            continue

                        if ScheduleConstraints.is_surgeon_available(
                                self.surgeon_timelines[surgeon.id], start_slot, duration
                        ) and ScheduleConstraints.check_surgeon_max_consecutive(
                            self.surgeon_timelines[surgeon.id], start_slot, duration
                        ):
                            assigned_surgeon_id = surgeon.id
                            break

                if not assigned_surgeon_id and self.surgeons:
                    continue  # Müsait cerrah bulunamadıysa bu slot/salon seçeneğini atla

                # 3. Anestezi Ekibi Seçimi: Atanmış ekip varsa kontrol et, yoksa havuzdan müsait olanı bul
                assigned_team_id = None
                if op_team:
                    if ScheduleConstraints.is_anesthesia_available(
                            self.anesthesia_timelines[op_team.id], start_slot, duration
                    ):
                        assigned_team_id = op_team.id
                else:
                    for team in self.anesthesia_teams:
                        if ScheduleConstraints.is_anesthesia_available(
                                self.anesthesia_timelines[team.id], start_slot, duration
                        ):
                            assigned_team_id = team.id
                            break

                if not assigned_team_id and self.anesthesia_teams:
                    continue  # Müsait anestezi ekibi bulunamadıysa bu slot/salon seçeneğini atla

                return {
                    'room_id': room.id,
                    'surgeon_id': assigned_surgeon_id,
                    'team_id': assigned_team_id,
                    'start_slot': start_slot
                }

        return None

    def save_schedule(self):
        updated_operations = []

        with transaction.atomic():
            for op in self.operations:
                if getattr(op, 'is_scheduled_temp', False):
                    op.room_id = op.assigned_room_id

                    if getattr(op, 'assigned_surgeon_id', None):
                        op.surgeon_id = op.assigned_surgeon_id

                    if getattr(op, 'assigned_team_id', None):
                        if hasattr(op, 'anesthesia_team_id'):
                            op.anesthesia_team_id = op.assigned_team_id
                        elif hasattr(op, 'anesthesia_id'):
                            op.anesthesia_id = op.assigned_team_id

                    op.start_slot = op.assigned_start_slot
                    op.is_scheduled = True
                    op.scheduled_date = self.date_obj.date()
                    updated_operations.append(op)

            if updated_operations:
                # Django bulk_update, '_id' uzantısını değil modeldeki alan adlarını ('room', 'surgeon') kabul eder
                model_field_names = [f.name for f in PatientOperation._meta.fields]

                possible_fields = ['room', 'surgeon', 'anesthesia_team', 'anesthesia', 'start_slot', 'is_scheduled',
                                   'scheduled_date']
                fields_to_update = [f for f in possible_fields if f in model_field_names]

                PatientOperation.objects.bulk_update(
                    updated_operations,
                    fields_to_update
                )

        return len(updated_operations)