from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.models import PatientOperation,OperatingRoom,Surgeon,AnesthesiaTeam
from api.serializers import RoomSerializer
from algorithm.optimizer import HospitalScheduler
from api.utils import slot_to_time_string

class RunSchedulerView(APIView):

    def post(self,request):
        operations = list(PatientOperation.objects.all())
        rooms=list(OperatingRoom.objects.all())
        surgeons=list(Surgeon.objects.all())
        anesthesia_teams=list(AnesthesiaTeam.objects.all())

        if not operations:
            return Response(
                {"detail":"Planlanacak açık ameliyat bulunamadı"},
            status=status.HTTP_400_BAD_REQUEST
            )
        if not rooms or not surgeons:
            return Response(
                {"detail":"Algoritmanın çalışması için ooda ve cerrah verileri eksik."},
                status=status.HTTP_400_BAD_REQUEST
            )

        scheduler=HospitalScheduler(
            operations=operations,
            rooms=rooms,
            surgeons=surgeons,
            anesthesia_teams=anesthesia_teams
        )
        result=scheduler.solve()

        placed_ops=result["placed"]
        for op in placed_ops:
            op.save()

        placed_summary = [
            {
                "operation_id": op.id,
                "patient_name": getattr(op, 'patient_name', f"Operation #{op.id}"),
                "assigned_room_id": op.required_room.id if op.required_room else None,
                "start_slot": op.start_slot,
                "duration_slot": op.duration_slot,
                "time_range": slot_to_time_string(op.start_slot, op.duration_slot)  # Örn: "08:00 - 09:30"
            }
            for op in placed_ops
        ]
        unplaced_summary=[
            {
                "operation_id":op.id,
                "priority":op.priority,
                "reason":"Uygun boş slot,oda veya ekip bulunamadı."
            }
            for op in result["unplaced"]
        ]
        return Response(
            {
                "message":"planlama algoritması başarıyla çalıştırıldı",
                "total_processed":len(operations),
                "placed_count":len(placed_ops),
                "unplaced_count":len(result["unplaced"]),
                "placed_operations":placed_summary,
                "unplaced_operations":unplaced_summary
                },
            status=status.HTTP_200_OK
        )








