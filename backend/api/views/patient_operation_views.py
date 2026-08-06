from api.models.patient_operation import PatientOperation
from api.serializers.patient_operation_serializer import PatientOperationSerializer
from .base_views import BaseViewSet

class PatientOperationViewSet(BaseViewSet):
    queryset=PatientOperation.objects.all()
    serializer_class=PatientOperationSerializer
    