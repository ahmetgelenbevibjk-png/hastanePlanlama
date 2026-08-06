from .models import AnesthesiaTeam
from base.serializers import BaseModelSerializer
class AnesthesiaSerializer(BaseModelSerializer):
    class Meta:
        model =AnesthesiaTeam
        fields='__all__'
