from rest_framework import serializers
from api.models.patient_operation import PatientOperation
from .base_serializer import BaseModelSerializer
from .surgeon_serializer import SurgeonSerializer
from .room_serializer import RoomSerializer
from .anesthesia_serializer import AnesthesiaSerializer

class PatientOperationSerializer(BaseModelSerializer):

    class Meta:
        model=PatientOperation
        fields='__all__'
