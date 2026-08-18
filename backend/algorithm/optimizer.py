from .constraints import can_assign_operation
from .penalties import calculate_assignment_penalty
from .constants import (
    PRIORITY_WEIGHTS,
    DEFAULT_TOTAL_SLOTS,
    SLOT_DURATION_MINUTES,
    DEFAULT_UNASSIGNED_PENALTY,
    DEFAULT_MAX_PENALTY_LIMIT,
    ALTERNATIVE_MAX_PENALTY_LIMIT,
    HIGH_PRIORITY_THRESHOLD,
    DEFAULT_DAY_NAME,
    DEFAULT_NUM_CANDIDATES,
    STRATEGY_CONFIGS,
    max_tolerable_penalty
)


def calculate_fitness_percentage(total_penalty,max_tolerable_penalty):

    if total_penalty >=max_tolerable_penalty:
        return 0.0
    fitness = max_tolerable_penalty - total_penalty
    return round(max(0.0, float(fitness)), 2)

class ScheduleOptimizer:

    def __init__(self,total_slots=DEFAULT_TOTAL_SLOTS):
        self.total_slots=total_slots

    def _get_op_priority(self,op):
        p=getattr(op,'priority','')
        if not p:
            return 0
        return PRIORITY_WEIGHTS.get(str(p).upper(),0)

    def _get_op_duration(self, op):
        dur = getattr(op, 'duration_slot', None)
        if dur is not None:
            return int(dur)
        raw_dur = getattr(op, 'duration', None)
        if raw_dur is not None:
            return max(1, int(raw_dur) // SLOT_DURATION_MINUTES)
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
                self.assign_operation_to_schedule(
                    operation=op,
                    slot=getattr(op, 'start_slot', 0),
                    room=getattr(op, 'room', None),
                    surgeon=getattr(op, 'surgeon', None),
                    anesthesia=getattr(op, 'anesthesia', None),
                    room_schedule=room_schedule,
                    surgeon_schedule=surgeon_schedule,
                    anesthesia_schedule=anesthesia_schedule
                )
        return room_schedule, surgeon_schedule, anesthesia_schedule

    def find_best_slot_for_operation(self, operation, rooms, surgeons, anesthesias, day_name,
                                     room_schedule, surgeon_schedule, anesthesia_schedule):

        best_option = None
        lowest_penalty = float('inf')

        for slot in range(self.total_slots):
            for room in rooms:
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


                            penalty = calculate_assignment_penalty(
                                operation=operation,
                                surgeon=surgeon,
                                room=room,
                                anesthesia=anesthesia,
                                start_slot=slot,
                                room_schedule=room_schedule,
                                surgeon_schedule=surgeon_schedule
                            )

                            if penalty < lowest_penalty:
                                lowest_penalty = penalty
                                best_option = (slot, room, surgeon, anesthesia, penalty)

                                if penalty == 0:
                                    return slot, room, surgeon, anesthesia, penalty

        if best_option:
            return best_option
        return None, None, None, None, None

    def assign_operation_to_schedule(self, operation, slot, room, surgeon, anesthesia,
                                     room_schedule, surgeon_schedule, anesthesia_schedule):
        if not all([room, surgeon, anesthesia]):
            return

        duration = self._get_op_duration(operation)
        room_id = room.id if hasattr(room, 'id') else room
        surgeon_id = surgeon.id if hasattr(surgeon, 'id') else surgeon
        anesthesia_id = anesthesia.id if hasattr(anesthesia, 'id') else anesthesia
        op_id = operation.id if hasattr(operation, 'id') else operation

        for offset in range(duration):
            curr_slot = slot + offset
            if curr_slot < self.total_slots:
                room_schedule[room_id][curr_slot] = op_id
                surgeon_schedule[surgeon_id][curr_slot] = op_id
                anesthesia_schedule[anesthesia_id][curr_slot] = op_id

    def remove_operation_from_schedule(self, operation, slot, room, surgeon, anesthesia,
                                       room_schedule, surgeon_schedule, anesthesia_schedule):
        duration = self._get_op_duration(operation)
        room_id = room.id if hasattr(room, 'id') else room
        surgeon_id = surgeon.id if hasattr(surgeon, 'id') else surgeon
        anesthesia_id = anesthesia.id if hasattr(anesthesia, 'id') else anesthesia

        for offset in range(duration):
            curr_slot = slot + offset
            if curr_slot < self.total_slots:
                room_schedule[room_id][curr_slot] = None
                surgeon_schedule[surgeon_id][curr_slot] = None
                anesthesia_schedule[anesthesia_id][curr_slot] = None

    def _apply_local_search(self, assigned_operations, rooms, surgeons, anesthesias, day_name,
                            room_schedule, surgeon_schedule, anesthesia_schedule):
        assigned_operations.sort(key=lambda x: x['penalty'], reverse=True)

        for i in range(len(assigned_operations)):
            op_data = assigned_operations[i]

            if op_data['penalty'] == 0:
                continue

                # Operasyonu geçici olarak çizelgeden çıkar
            self.remove_operation_from_schedule(
                op_data['operation'], op_data['start_slot'], op_data['room'],
                op_data['surgeon'], op_data['anesthesia'],
                room_schedule, surgeon_schedule, anesthesia_schedule
            )
            new_slot, new_room, new_surgeon, new_anes, new_penalty = self.find_best_slot_for_operation(
                operation=op_data['operation'],
                rooms=rooms,
                surgeons=surgeons,
                anesthesias=anesthesias,
                day_name=day_name,
                room_schedule=room_schedule,
                surgeon_schedule=surgeon_schedule,
                anesthesia_schedule=anesthesia_schedule
            )

            if new_slot is not None and new_penalty < op_data['penalty']:
                self.assign_operation_to_schedule(
                    op_data['operation'], new_slot, new_room, new_surgeon, new_anes,
                    room_schedule, surgeon_schedule, anesthesia_schedule
                )
                assigned_operations[i] = {
                    'operation': op_data['operation'],
                    'start_slot': new_slot,
                    'room': new_room,
                    'surgeon': new_surgeon,
                    'anesthesia': new_anes,
                    'penalty': new_penalty
                }
            else:
                self.assign_operation_to_schedule(
                    op_data['operation'], op_data['start_slot'], op_data['room'],
                    op_data['surgeon'], op_data['anesthesia'],
                    room_schedule, surgeon_schedule, anesthesia_schedule
                )

            return assigned_operations

    def optimize_with_alternatives(self, operations, rooms, surgeons, anesthesias, day_name=DEFAULT_DAY_NAME,
                                   num_candidates=DEFAULT_NUM_CANDIDATES):
        candidates = []

        strategies = [
            {**STRATEGY_CONFIGS[0], 'sort': lambda ops: self.sort_operations_by_priority(ops)},
            {**STRATEGY_CONFIGS[1], 'sort': lambda ops: sorted(ops, key=lambda op: (
                self._get_op_priority(op) >= HIGH_PRIORITY_THRESHOLD, self._get_op_priority(op)), reverse=True)},
            {**STRATEGY_CONFIGS[2],
             'sort': lambda ops: sorted(ops, key=lambda op: self._get_op_duration(op), reverse=True)},
            {**STRATEGY_CONFIGS[3],
             'sort': lambda ops: sorted(ops, key=lambda op: -self._get_op_duration(op), reverse=True)},
            {**STRATEGY_CONFIGS[4], 'sort': lambda ops: sorted(ops, key=lambda op: (
                getattr(getattr(op, 'surgeon', None), 'id', 0), self._get_op_priority(op)), reverse=True)}
        ]

        for i in range(num_candidates):
            strat = strategies[i % len(strategies)]
            sorted_ops = strat['sort'](operations)

            room_schedule, surgeon_schedule, anesthesia_schedule = self.initialize_schedules(rooms, surgeons,
                                                                                             anesthesias)
            assigned_operations = []
            unassigned_operations = []

            for op in sorted_ops:
                slot, room, surgeon, anesthesia, penalty = self.find_best_slot_for_operation(
                    operation=op, rooms=rooms, surgeons=surgeons, anesthesias=anesthesias,
                    day_name=day_name, room_schedule=room_schedule,
                    surgeon_schedule=surgeon_schedule, anesthesia_schedule=anesthesia_schedule
                )

                if slot is not None:
                    self.assign_operation_to_schedule(
                        op, slot, room, surgeon, anesthesia,
                        room_schedule, surgeon_schedule, anesthesia_schedule
                    )
                    assigned_operations.append({
                        'operation': op, 'start_slot': slot, 'room': room,
                        'surgeon': surgeon, 'anesthesia': anesthesia, 'penalty': penalty
                    })
                else:
                    unassigned_operations.append(op)

            assigned_operations = self._apply_local_search(
                assigned_operations, rooms, surgeons, anesthesias, day_name,
                room_schedule, surgeon_schedule, anesthesia_schedule
            )

            total_schedule_penalty = sum(item['penalty'] * strat['penalty_multiplier'] for item in assigned_operations)
            total_schedule_penalty += len(unassigned_operations) * strat['unassigned_penalty']

            fitness_score = calculate_fitness_percentage(total_schedule_penalty, max_tolerable_penalty=ALTERNATIVE_MAX_PENALTY_LIMIT)

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

        candidates.sort(key=lambda x: x['fitness_score'], reverse=True)

        return {
            'best_plan': candidates[0],
            'all_candidates': candidates
        }