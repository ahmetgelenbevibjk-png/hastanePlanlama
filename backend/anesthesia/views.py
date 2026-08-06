from .models import AnesthesiaTeam
from .serializers import AnesthesiaSerializer
from base.views import BaseViewSet

class AnesthesiaTeamViewSet(BaseViewSet):
    queryset = AnesthesiaTeam.objects.all()
    serializer_class = AnesthesiaSerializer