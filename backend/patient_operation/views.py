from .models import PatientOperation
from .serializers import PatientOperationSerializer
from base.views import BaseViewSet

class PatientOperationViewSet(BaseViewSet):
    queryset=PatientOperation.objects.all()
    serializer_class=PatientOperationSerializer
    