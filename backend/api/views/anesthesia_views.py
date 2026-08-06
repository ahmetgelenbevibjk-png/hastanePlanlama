from api.models.anesthesia import AnesthesiaTeam
from api.serializers.anesthesia_serializer import AnesthesiaSerializer
from .base_views import BaseViewSet
class AnesthesiaTeamViewSet(BaseViewSet):
    queryset=AnesthesiaTeam.objects.all()
    serializer_class=AnesthesiaSerializer
