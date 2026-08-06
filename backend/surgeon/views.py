from .models import Surgeon
from .serializers import SurgeonSerializer
from base.views import BaseViewSet

class SurgeonViewSet(BaseViewSet):
    queryset=Surgeon.objects.all()
    serializer_class=SurgeonSerializer
