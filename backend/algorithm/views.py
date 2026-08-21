from datetime import datetime
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from patient_operation.models import PatientOperation as Operation
from room.models import OperatingRoom
from surgeon.models import Surgeon
from anesthesia.models import AnesthesiaTeam

from .optimizer import ScheduleOptimizer
from .constants import DEFAULT_TOTAL_SLOTS, DEFAULT_FALLBACK_DAY, DEFAULT_NUM_CANDIDATES, DAYS_TR
from .constraints import can_assign_operation
from .penalties import calculate_assignment_penalty


def fmt_op(item):
    """Atanmış ameliyat nesnesini sözlüğe dönüştürür."""
    op, r, s, a = item['operation'], item['room'], item['surgeon'], item['anesthesia']
    return {
        'operation_id': getattr(op, 'id', None),
        'patient_name': getattr(op, 'patient_name', f"Hasta #{getattr(op, 'id', '')}"),
        'operation_name': getattr(op, 'operation_name', 'Ameliyat'),
        'priority': getattr(op, 'priority', 'NORMAL'),
        'start_slot': item['start_slot'],
        'duration_slot': getattr(op, 'duration_slot', 1),
        'penalty': item.get('penalty', 0),
        'room_id': getattr(r, 'id', None),
        'room_name': getattr(r, 'name', 'Salon Yok'),
        'surgeon_id': getattr(s, 'id', None),
        'surgeon_name': getattr(s, 'name', getattr(s, 'full_name', 'Cerrah Yok')),
        'anesthesia_id': getattr(a, 'id', None),
        'anesthesia_name': getattr(a, 'name', 'Ekip Yok')
    }


class ScheduleOptimizeView(APIView):

    def post(self, request):
        selected_date = request.data.get('date')
        d_str = str(selected_date or '')
        
        # 1. Güvenli Gün Tespiti (HTTP 500 çökmesini önler)
        day_name = request.data.get('day_name')
        if not day_name and '-' in d_str:
            try:
                day_name = DAYS_TR[datetime.strptime(d_str.split('T')[0], '%Y-%m-%d').weekday()]
            except ValueError:
                day_name = DEFAULT_FALLBACK_DAY
        else:
            day_name = day_name or DEFAULT_FALLBACK_DAY

        ops = list(Operation.objects.filter(is_active=True))
        if not ops:
            return Response({"message": "Aktif operasyon bulunamadı."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Temizlik ve kaynak çekimi
        Operation.objects.filter(is_active=True).update(is_scheduled=False, room=None, start_slot=None, surgeon=None, anesthesia=None)
        rooms = list(OperatingRoom.objects.filter(is_active=True))
        surgeons = list(Surgeon.objects.filter(is_active=True) if hasattr(Surgeon, 'is_active') else Surgeon.objects.all())
        anesthesias = list(AnesthesiaTeam.objects.filter(is_active=True) if hasattr(AnesthesiaTeam, 'is_active') else AnesthesiaTeam.objects.all())

        # 3. Optimizasyon (DEFAULT_NUM_CANDIDATES yedeklemesi eklendi)
        num_candidates = request.data.get('num_candidates') or DEFAULT_NUM_CANDIDATES
        results = ScheduleOptimizer(DEFAULT_TOTAL_SLOTS).optimize_with_alternatives(
            ops, rooms, surgeons, anesthesias, day_name, num_candidates
        )
        best = results.get('best_plan')
        if not best:
            return Response({"message": "Uygun plan bulunamadı."}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Veritabanı toplu kaydı
        with transaction.atomic():
            for item in best['assigned']:
                op = item['operation']
                op.room, op.start_slot, op.surgeon, op.anesthesia, op.is_scheduled = (
                    item['room'], item['start_slot'], item['surgeon'], item['anesthesia'], True
                )
                if hasattr(op, 'scheduled_date') and selected_date:
                    op.scheduled_date = selected_date
                op.save()

        return Response({
            'status': 'success',
            'day': day_name,
            'fitness_score': best['fitness_score'],
            'assigned': [fmt_op(x) for x in best['assigned']],
            'unassigned': [{'operation_id': op.id, 'patient_name': getattr(op, 'patient_name', '')} for op in best['unassigned']],
            'candidates': [
                {
                    'id': c['candidate_id'],
                    'name': c['strategy_name'],
                    'fitness_score': c['fitness_score'],
                    'total_penalty': c['total_penalty'],
                    'assigned': [fmt_op(x) for x in c['assigned']]
                } for c in results['all_candidates']
            ]
        }, status=status.HTTP_200_OK)


class ManualScheduleUpdateView(APIView):

    def post(self, request):
        op_id, r_id, slot = request.data.get('operation_id'), request.data.get('target_room_id'), request.data.get('target_slot')
        if None in (op_id, r_id, slot):
            return Response({'success': False, 'message': 'Eksik parametre!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            op = Operation.objects.get(id=op_id)
            room = OperatingRoom.objects.get(id=r_id)
        except (Operation.DoesNotExist, OperatingRoom.DoesNotExist):
            return Response({'success': False, 'message': 'Geçersiz ID!'}, status=status.HTTP_404_NOT_FOUND)

        # Harita oluşturma
        r_sched, s_sched, a_sched = {}, {}, {}
        for scheduled in Operation.objects.filter(is_active=True, is_scheduled=True).exclude(id=op.id):
            if scheduled.start_slot is None:
                continue
            slots = list(range(scheduled.start_slot, scheduled.start_slot + getattr(scheduled, 'duration_slot', 1)))
            if scheduled.room_id: r_sched.setdefault(scheduled.room_id, []).extend(slots)
            if scheduled.surgeon_id: s_sched.setdefault(scheduled.surgeon_id, []).extend(slots)
            if scheduled.anesthesia_id: a_sched.setdefault(scheduled.anesthesia_id, []).extend(slots)

        s, a = getattr(op, 'surgeon', None), getattr(op, 'anesthesia', None)
        if not can_assign_operation(op, s, room, a, slot, request.data.get('day_name', 'Pazartesi'), r_sched, s_sched, a_sched):
            return Response({'success': False, 'message': 'Kısıt ihlali nedeniyle taşıma engellendi.'}, status=status.HTTP_400_BAD_REQUEST)

        op.room, op.start_slot, op.is_scheduled = room, slot, True
        op.save()

        penalty = calculate_assignment_penalty(op, s, room, a, slot, r_sched, s_sched)
        return Response({'success': True, 'target_slot': slot, 'target_room_id': r_id, 'new_penalty': penalty}, status=status.HTTP_200_OK)