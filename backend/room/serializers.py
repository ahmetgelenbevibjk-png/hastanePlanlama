from .models import OperatingRoom
from base.serializers import BaseModelSerializer
class RoomSerializer(BaseModelSerializer):
    class Meta:
        model=OperatingRoom
        fields='__all__'