import random
from .constraints import can_assign_operation
from .penalties import calculate_assignment_penalty, calculate_fitness_percentage


class ScheduleOptimizer:

    PRIORITY_WEIGHTS = {
        'KRITIK': 4,
        'CRITICAL': 4,
        'YÜKSEK': 3,
        'HIGH': 3,
        'NORMAL': 2,
        'MEDIUM': 2,
        'DÜŞÜK': 1,
        'LOW': 1,
    }

    def __init__(self, total_slots=20):
        self.total_slots = total_slots

    def _get_op_priority(self, op):
        p = getattr(op, 'priority', '')
        if not p:
            return 0
        return self.PRIORITY_WEIGHTS.get(str(p).upper(), 0)

    def _get_op_duration(self, op):
        dur = getattr(op, 'duration_slot', None)
        if dur is not None:
            return int(dur)
        raw_dur = getattr(op, 'duration', None)
        if raw_dur is not None:
            return max(1, int(raw_dur) // 30)
        return 1

    def sort_operations_by_priority(self, operations):
        return sorted(
            operations,
            key=lambda op: self._get_op_priority(op),
            reverse=True
        )

    def initialize_schedules(self, rooms, surgeons, anesthesias, pre_assigned_operations=None):
        room_schedule = {r.id if hasattr(r, 'id') else r: [None] * self.total_slots for r in rooms}
        surgeon_schedule = {s.id if hasattr(s, 'id') else s: [None] * self.total_slots for s in surgeons}
        anesthesia_schedule = {a.id if hasattr(a, 'id') else a: [None] * self.total_slots for a in anesthesias}

        if pre_assigned_operations:
            for op in pre_assigned_operations:
                r_id = getattr(op, 'room_id', None) or getattr(getattr(op, 'room', None), 'id', None)
                s_id = getattr(op, 'surgeon_id', None) or getattr(getattr(op, 'surgeon', None), 'id', None)
                a_id = getattr(op, 'anesthesia_id', None) or getattr(getattr(op, 'anesthesia', None), 'id', None)
                start_slot = getattr(op, 'start_slot', None)
                duration = self._get_op_duration(op)
                op_id = getattr(op, 'id', op)

                if r_id and start_slot is not None:
                    for offset in range(duration):
                        curr_slot = start_slot + offset
                        if curr_slot < self.total_slots:
                            if r_id in room_schedule:
                                room_schedule[r_id][curr_slot] = op_id
                            if s_id and s_id in surgeon_schedule:
                                surgeon_schedule[s_id][curr_slot] = op_id
                            if a_id and a_id in anesthesia_schedule:
                                anesthesia_schedule[a_id][curr_slot] = op_id

        return room_schedule, surgeon_schedule, anesthesia_schedule

    def find_best_slot_for_operation(self, operation, rooms, surgeons, anesthesias, day_name,
                                    room_schedule, surgeon_schedule, anesthesia_schedule,
                                    shuffle_rooms=False, shuffle_slots=False):
        best_option = None
        lowest_penalty = float('inf')

        room_list = list(rooms)
        if shuffle_rooms:
            random.shuffle(room_list)

        slot_list = list(range(self.total_slots))
        if shuffle_slots:
            # Belirli stratejilerde saatleri ters veya esnek tarayarak farklı slotlara yerleşmesini sağla
            slot_list.sort(key=lambda x: random.random())

        for slot in slot_list:
            for room in room_list:
                for surgeon in surgeons:
                    for anesthesia in anesthesias:
                        if can_assign_operation(
                            operation=operation,
                            surgeon=surgeon,
                            room=room,
                            anesthesia=anesthesia,
                            start_slot=slot,
                            day_name=day_name,
                            room_schedule=room_schedule,
                            surgeon_schedule=surgeon_schedule,
                            anesthesia_schedule=anesthesia_schedule,
                            total_slots=self.total_slots
                        ):
                            penalty = calculate_assignment_penalty(operation, slot, surgeon, surgeon_schedule)

                            if penalty < lowest_penalty:
                                lowest_penalty = penalty
                                best_option = (slot, room, surgeon, anesthesia, penalty)

                                if penalty == 0 and not shuffle_rooms and not shuffle_slots:
                                    return slot, room, surgeon, anesthesia, penalty

        if best_option:
            return best_option[0], best_option[1], best_option[2], best_option[3], best_option[4]
        return None, None, None, None, None

    def assign_operation_to_schedule(self, operation, slot, room, surgeon, anesthesia,
                                     room_schedule, surgeon_schedule, anesthesia_schedule):
        duration = self._get_op_duration(operation)

        room_id = room.id if hasattr(room, 'id') else room
        surgeon_id = surgeon.id if hasattr(surgeon, 'id') else surgeon
        anesthesia_id = anesthesia.id if hasattr(anesthesia, 'id') else anesthesia
        op_id = operation.id if hasattr(operation, 'id') else operation

        if room_id not in room_schedule:
            room_schedule[room_id] = [None] * self.total_slots
        if surgeon_id not in surgeon_schedule:
            surgeon_schedule[surgeon_id] = [None] * self.total_slots
        if anesthesia_id not in anesthesia_schedule:
            anesthesia_schedule[anesthesia_id] = [None] * self.total_slots

        for offset in range(duration):
            curr_slot = slot + offset
            if curr_slot < self.total_slots:
                room_schedule[room_id][curr_slot] = op_id
                surgeon_schedule[surgeon_id][curr_slot] = op_id
                anesthesia_schedule[anesthesia_id][curr_slot] = op_id

    def optimize_schedule(self, operations, rooms, surgeons, anesthesias, day_name="Pazartesi",
                          pre_assigned_operations=None):
        sorted_ops = self.sort_operations_by_priority(operations)

        room_schedule, surgeon_schedule, anesthesia_schedule = self.initialize_schedules(
            rooms, surgeons, anesthesias, pre_assigned_operations=pre_assigned_operations
        )

        assigned_operations = []
        unassigned_operations = []
        total_schedule_penalty = 0

        for op in sorted_ops:
            slot, room, surgeon, anesthesia, penalty = self.find_best_slot_for_operation(
                operation=op,
                rooms=rooms,
                surgeons=surgeons,
                anesthesias=anesthesias,
                day_name=day_name,
                room_schedule=room_schedule,
                surgeon_schedule=surgeon_schedule,
                anesthesia_schedule=anesthesia_schedule
            )

            if slot is not None:
                self.assign_operation_to_schedule(
                    op, slot, room, surgeon, anesthesia,
                    room_schedule, surgeon_schedule, anesthesia_schedule
                )

                total_schedule_penalty += penalty
                assigned_operations.append({
                    'operation': op,
                    'start_slot': slot,
                    'room': room,
                    'surgeon': surgeon,
                    'anesthesia': anesthesia,
                    'penalty': penalty
                })
            else:
                unassigned_operations.append(op)
                total_schedule_penalty += 50

        max_penalty_limit = max(200, len(operations) * 50)
        fitness_score = calculate_fitness_percentage(total_schedule_penalty, max_tolerable_penalty=max_penalty_limit)
        return {
            'assigned': assigned_operations,
            'unassigned': unassigned_operations,
            'fitness_score': fitness_score,
            'schedules': {
                'room': room_schedule,
                'surgeon': surgeon_schedule,
                'anesthesia': anesthesia_schedule
            }
        }

    def optimize_with_alternatives(self, operations, rooms, surgeons, anesthesias, day_name="Pazartesi",
                                   num_candidates=5):
        candidates = []

        # Her stratejinin hedefi ve ceza çarpanları farklılaştırıldı
        strategies = [
            {
                'name': 'Öncelik Odaklı (Standart)',
                'sort': lambda ops: sorted(ops, key=lambda op: self._get_op_priority(op), reverse=True),
                'unassigned_penalty': 50,
                'penalty_multiplier': 1.0
            },
            {
                'name': 'Kritik Vaka Hassasiyeti',
                'sort': lambda ops: sorted(ops,
                                           key=lambda op: (self._get_op_priority(op) >= 3, self._get_op_priority(op)),
                                           reverse=True),
                'unassigned_penalty': 80,  # Kritik vaka dışarıda kalırsa yüksek ceza keser
                'penalty_multiplier': 1.3
            },
            {
                'name': 'Salon Kapasite Verimliliği',
                'sort': lambda ops: sorted(ops, key=lambda op: self._get_op_duration(op), reverse=True),
                'unassigned_penalty': 40,  # Uzun ameliyatları yerleştirmeyi ödüllendirir
                'penalty_multiplier': 0.8
            },
            {
                'name': 'Hızlı Sirkülasyon (Vaka Sayısı)',
                'sort': lambda ops: sorted(ops, key=lambda op: -self._get_op_duration(op), reverse=True),
                'unassigned_penalty': 30,  # Çok sayıda ameliyat bitirmeye odaklanır
                'penalty_multiplier': 0.6
            },
            {
                'name': 'Dengeli Cerrah Programı',
                'sort': lambda ops: sorted(ops, key=lambda op: (getattr(getattr(op, 'surgeon', None), 'id', 0),
                                                                self._get_op_priority(op)), reverse=True),
                'unassigned_penalty': 45,
                'penalty_multiplier': 1.0
            }
        ]

        for i in range(num_candidates):
            try:
                strat = strategies[i % len(strategies)]
                sorted_ops = strat['sort'](operations)

                room_schedule, surgeon_schedule, anesthesia_schedule = self.initialize_schedules(rooms, surgeons,
                                                                                                 anesthesias)
                assigned_operations = []
                unassigned_operations = []
                total_schedule_penalty = 0

                for op in sorted_ops:
                    slot, room, surgeon, anesthesia, penalty = self.find_best_slot_for_operation(
                        operation=op,
                        rooms=rooms,
                        surgeons=surgeons,
                        anesthesias=anesthesias,
                        day_name=day_name,
                        room_schedule=room_schedule,
                        surgeon_schedule=surgeon_schedule,
                        anesthesia_schedule=anesthesia_schedule
                    )

                    if slot is not None:
                        self.assign_operation_to_schedule(
                            op, slot, room, surgeon, anesthesia,
                            room_schedule, surgeon_schedule, anesthesia_schedule
                        )
                        # Stratejinin ceza çarpanını uygula
                        total_schedule_penalty += int(penalty * strat['penalty_multiplier'])
                        assigned_operations.append({
                            'operation': op,
                            'start_slot': slot,
                            'room': room,
                            'surgeon': surgeon,
                            'anesthesia': anesthesia,
                            'penalty': penalty
                        })
                    else:
                        unassigned_operations.append(op)
                        # Stratejiye özel atanamama cezası
                        total_schedule_penalty += strat['unassigned_penalty']

                # Skor skalası ölçeklendirmesi
                max_penalty_limit = 250
                fitness_score = calculate_fitness_percentage(total_schedule_penalty,
                                                             max_tolerable_penalty=max_penalty_limit)

                candidates.append({
                    'candidate_id': i + 1,
                    'strategy_name': strat['name'],
                    'fitness_score': fitness_score,
                    'total_penalty': total_schedule_penalty,
                    'assigned_count': len(assigned_operations),
                    'unassigned_count': len(unassigned_operations),
                    'assigned': assigned_operations,
                    'unassigned': unassigned_operations,
                    'schedules': {
                        'room': room_schedule,
                        'surgeon': surgeon_schedule,
                        'anesthesia': anesthesia_schedule
                    }
                })
            except Exception as e:
                print(f"Aday plan #{i + 1} oluşturulurken hata:", str(e))
                continue

        if not candidates:
            default_res = self.optimize_schedule(operations, rooms, surgeons, anesthesias, day_name)
            candidates.append({
                'candidate_id': 1,
                'strategy_name': 'Standart Plan',
                'fitness_score': default_res['fitness_score'],
                'total_penalty': 0,
                'assigned_count': len(default_res['assigned']),
                'unassigned_count': len(default_res['unassigned']),
                'assigned': default_res['assigned'],
                'unassigned': default_res['unassigned'],
                'schedules': default_res['schedules']
            })

        # Skorları en yüksekten en düşüğe sırala
        candidates.sort(key=lambda x: x['fitness_score'], reverse=True)

        return {
            'best_plan': candidates[0],
            'all_candidates': candidates
        }