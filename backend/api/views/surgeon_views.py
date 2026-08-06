from api.models.surgeon import Surgeon
from api.serializers.surgeon_serializer import SurgeonSerializer
from .base_views import BaseViewSet

class SurgeonViewSet(BaseViewSet):
    queryset=Surgeon.objects.all()
    serializer_class=SurgeonSerializer
