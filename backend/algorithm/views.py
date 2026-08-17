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

        # Mevcut atamaları bellekte sıfırla
        for op in all_operations:
            op.is_scheduled = False
            op.room = None
            op.start_slot = None
            op.surgeon = None
            op.anesthesia = None

        pending_operations = all_operations

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

        # 5 farklı alternatif plan simüle ediliyor
        optimizer = ScheduleOptimizer(total_slots=20)
        results = optimizer.optimize_with_alternatives(
            operations=pending_operations,
            rooms=rooms,
            surgeons=surgeons,
            anesthesias=anesthesias,
            day_name=day_name,
            num_candidates=5
        )

        best_plan = results['best_plan']

        # En iyi planı veritabanına kaydet
        try:
            with transaction.atomic():
                for item in best_plan['assigned']:
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

        # ORM nesnelerini JSON'a uygun sözlüklere dönüştüren yardımcı fonksiyon
        def format_assigned_list(assigned_list):
            formatted = []
            for item in assigned_list:
                op = item['operation']
                room = item['room']
                surgeon = item['surgeon']
                anesthesia = item['anesthesia']
                start_slot = item['start_slot']

                formatted.append({
                    'operation_id': getattr(op, 'id', None),
                    'patient_name': getattr(op, 'patient_name', f"Hasta #{getattr(op, 'id', '')}"),
                    'operation_name': getattr(op, 'operation_name', 'Ameliyat'),
                    'priority': getattr(op, 'priority', 'NORMAL'),
                    'start_slot': start_slot,
                    'duration_slot': getattr(op, 'duration_slot', 1),
                    'penalty': item.get('penalty', 0),
                    'room_id': getattr(room, 'id', None) if room else None,
                    'room_name': getattr(room, 'name', f"OR-{getattr(room, 'id', '')}") if room else "Salon Yok",
                    'surgeon_id': getattr(surgeon, 'id', None) if surgeon else None,
                    'surgeon_name': getattr(surgeon, 'name', getattr(surgeon, 'full_name', f"Dr. {getattr(surgeon, 'id', '')}")) if surgeon else "Cerrah Yok",
                    'anesthesia_id': getattr(anesthesia, 'id', None) if anesthesia else None,
                    'anesthesia_name': getattr(anesthesia, 'name', getattr(anesthesia, 'team_name', f"Ekip {getattr(anesthesia, 'id', '')}")) if anesthesia else "Ekip Yok"
                })
            return formatted

        # Aday senaryoları JSON serileştirmeye uygun hale getirme
        formatted_candidates = []
        for c in results['all_candidates']:
            formatted_candidates.append({
                'id': c['candidate_id'],
                'name': c['strategy_name'],
                'fitness_score': c['fitness_score'],
                'total_penalty': c['total_penalty'],
                'assigned_count': c['assigned_count'],
                'unassigned_count': c['unassigned_count'],
                'assigned': format_assigned_list(c['assigned'])
            })

        formatted_assigned = format_assigned_list(best_plan['assigned'])

        formatted_unassigned = [
            {
                'operation_id': getattr(op, 'id', None),
                'patient_name': getattr(op, 'patient_name', f"Hasta #{getattr(op, 'id', '')}"),
                'operation_name': getattr(op, 'operation_name', 'Ameliyat'),
                'priority': getattr(op, 'priority', 'NORMAL'),
                'reason': 'Kısıtları sağlayan uygun slot veya kaynak bulunamadı.'
            }
            for op in best_plan['unassigned']
        ]

        return Response({
            'status': 'success',
            'day': day_name,
            'fitness_score': best_plan['fitness_score'],
            'assigned_count': len(formatted_assigned),
            'unassigned_count': len(formatted_unassigned),
            'assigned': formatted_assigned,
            'unassigned': formatted_unassigned,
            'candidates': formatted_candidates
        }, status=status.HTTP_200_OK)