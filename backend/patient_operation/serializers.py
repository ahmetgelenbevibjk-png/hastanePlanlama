from .models import PatientOperation
from base.serializers import BaseModelSerializer


class PatientOperationSerializer(BaseModelSerializer):

    class Meta:
        model=PatientOperation
        fields='__all__'
