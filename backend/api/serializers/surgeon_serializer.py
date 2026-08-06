from rest_framework import serializers
from api.models import Surgeon
from .base_serializer import BaseModelSerializer
class SurgeonSerializer(BaseModelSerializer):
    class Meta:
        model = Surgeon
        fields='__all__'