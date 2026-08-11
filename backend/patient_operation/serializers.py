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

    def get_surgeon_name(self,obj):
        return obj.surgeon.name if obj.surgeon else None

    def get_anesthesia_name(self,obj):
        return obj.anesthesia.name if obj.anesthesia else None

    def get_required_room_name(self,obj):
        return obj.required_room.name if obj.required_room else None