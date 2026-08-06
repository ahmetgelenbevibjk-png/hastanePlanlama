from .models import OperatingRoom
from .serializers import RoomSerializer
from base.views import BaseViewSet

class RoomViewSet(BaseViewSet):
    queryset=OperatingRoom.objects.all()
    serializer_class=RoomSerializer
