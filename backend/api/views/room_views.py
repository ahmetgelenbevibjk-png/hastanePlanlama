from api.models.room import OperatingRoom
from api.serializers.room_serializer import RoomSerializer
from .base_views import BaseViewSet

class RoomViewSet(BaseViewSet):
    queryset=OperatingRoom.objects.all()
    serializer_class=RoomSerializer
