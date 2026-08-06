from rest_framework import serializers
from api.models import AnesthesiaTeam
from .base_serializer import BaseModelSerializer
class AnesthesiaSerializer(BaseModelSerializer):
    class Meta:
        model =AnesthesiaTeam
        fields='__all__'
