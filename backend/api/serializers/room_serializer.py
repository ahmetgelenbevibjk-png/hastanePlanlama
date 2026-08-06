from rest_framework import serializers
from api.models import OperatingRoom
from .base_serializer import BaseModelSerializer
class RoomSerializer(BaseModelSerializer):
    class Meta:
        model=OperatingRoom
        fields='__all__'