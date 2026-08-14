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


class ScheduleOptimizeView(APIView):

    def post(self, request):
        selected_date = request.data.get('date')
        day_name = request.data.get('day_name')

        # Tarih formatı kontrolü
        if isinstance(selected_date, dict):
            selected_date_str = selected_date.get('date') or selected_date.get('formatted') or str(selected_date)
        else:
            selected_date_str = str(selected_date) if selected_date else None

        DAYS_TR = {
            0: 'Pazartesi', 1: 'Salı', 2: 'Çarşamba', 3: 'Perşembe',
            4: 'Cuma', 5: 'Cumartesi', 6: 'Pazar'
        }

        if selected_date_str and selected_date_str != 'None':
            try:
                if 'T' in selected_date_str:
                    selected_date_str = selected_date_str.split('T')[0]

                if '.' in selected_date_str:
                    date_obj = datetime.strptime(selected_date_str, '%d.%m.%Y')
                elif '-' in selected_date_str:
                    date_obj = datetime.strptime(selected_date_str, '%Y-%m-%d')
                else:
                    date_obj = None

                if date_obj:
                    day_name = DAYS_TR[date_obj.weekday()]
            except (ValueError, TypeError):
                pass

        if not day_name:
            day_name = 'Perşembe'

            # Tüm aktif operasyonları alıyoruz
        all_operations = list(Operation.objects.filter(is_active=True))

        if not all_operations:
            return Response(
                {"message": "Sistemde hiç aktif operasyon bulunamadı."},
                status=status.HTTP_400_BAD_REQUEST
            )

        for op in all_operations:
            op.is_scheduled = False
            op.room = None
            op.start_slot = None
            op.surgeon = None
            op.anesthesia = None

        pending_operations = all_operations
        pre_assigned_operations = []

        rooms = list(OperatingRoom.objects.filter(is_active=True))

        surgeons = list(
            Surgeon.objects.filter(is_active=True)
            if hasattr(Surgeon, 'is_active')
            else Surgeon.objects.all()
        )

        anesthesias = list(
            AnesthesiaTeam.objects.filter(is_active=True)
            if hasattr(AnesthesiaTeam, 'is_active')
            else AnesthesiaTeam.objects.all()
        )

        if not all_operations:
            return Response(
                {"message": "Sistemde hiç aktif operasyon bulunamadı."},
                status=status.HTTP_400_BAD_REQUEST
            )

        optimizer = ScheduleOptimizer(total_slots=20)
        results = optimizer.optimize_schedule(
            operations=pending_operations,
            rooms=rooms,
            surgeons=surgeons,
            anesthesias=anesthesias,
            day_name=day_name,
            pre_assigned_operations=pre_assigned_operations
        )

        try:
            with transaction.atomic():
                for item in results['assigned']:
                    op = item['operation']

                    op.room = item['room']
                    op.start_slot = item['start_slot']
                    op.surgeon = item['surgeon']
                    op.anesthesia = item['anesthesia']
                    op.is_scheduled = True

                    if hasattr(op, 'scheduled_date') and selected_date_str:
                        op.scheduled_date = selected_date_str

                    op.save()
        except Exception as e:
            print("Veritabanına kayıt hatası:", str(e))
            return Response(
                {"message": f"Planlama yapıldı ancak veritabanına kaydedilemedi: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        all_assigned_for_response = results['assigned'] + [
            {
                'operation': op,
                'start_slot': op.start_slot,
                'room': op.room,
                'surgeon': op.surgeon,
                'anesthesia': op.anesthesia
            }
            for op in pre_assigned_operations if op not in [i['operation'] for i in results['assigned']]
        ]

        formatted_assigned = []
        for item in all_assigned_for_response:
            op = item['operation']
            room = item['room']
            surgeon = item['surgeon']
            anesthesia = item['anesthesia']
            start_slot = item['start_slot']

            formatted_assigned.append({
                'operation_id': getattr(op, 'id', None),
                'patient_name': getattr(op, 'patient_name', f"Hasta #{getattr(op, 'id', '')}"),
                'operation_name': getattr(op, 'operation_name', 'Ameliyat'),
                'priority': getattr(op, 'priority', 'NORMAL'),
                'start_slot': start_slot,
                'duration_slot': getattr(op, 'duration_slot', 1),
                'room_id': getattr(room, 'id', None) if room else None,
                'room_name': getattr(room, 'name', f"OR-{getattr(room, 'id', '')}") if room else "Salon Yok",
                'surgeon_id': getattr(surgeon, 'id', None) if surgeon else None,
                'surgeon_name': getattr(surgeon, 'name', getattr(surgeon, 'full_name',
                                                                 f"Dr. {getattr(surgeon, 'id', '')}")) if surgeon else "Cerrah Yok",
                'anesthesia_id': getattr(anesthesia, 'id', None) if anesthesia else None,
                'anesthesia_name': getattr(anesthesia, 'name', getattr(anesthesia, 'team_name',
                                                                       f"Ekip {getattr(anesthesia, 'id', '')}")) if anesthesia else "Ekip Yok"
            })

        formatted_unassigned = [
            {
                'operation_id': getattr(op, 'id', None),
                'patient_name': getattr(op, 'patient_name', f"Hasta #{getattr(op, 'id', '')}"),
                'operation_name': getattr(op, 'operation_name', 'Ameliyat'),
                'priority': getattr(op, 'priority', 'NORMAL'),
                'reason': 'Kısıtları sağlayan uygun slot veya kaynak bulunamadı.'
            }
            for op in results['unassigned']
        ]

        return Response({
            'status': 'success',
            'day': day_name,
            'assigned_count': len(formatted_assigned),
            'unassigned_count': len(formatted_unassigned),
            'assigned': formatted_assigned,
            'unassigned': formatted_unassigned
        }, status=status.HTTP_200_OK)