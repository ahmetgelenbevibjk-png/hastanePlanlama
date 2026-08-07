from .models import PatientOperation
from base.serializers import BaseModelSerializer
from rest_framework import serializers

class PatientOperationSerializer(BaseModelSerializer):
    surgeon_name = serializers.ReadOnlyField(source='surgeon.name')
    anesthesia_name = serializers.ReadOnlyField(source='anesthesia.name')
    required_room_name = serializers.ReadOnlyField(source='required_room.name')

    class Meta:
        model=PatientOperation
        fields='__all__'
