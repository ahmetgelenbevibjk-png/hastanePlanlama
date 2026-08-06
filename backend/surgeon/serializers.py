from .models import Surgeon
from base.serializers import BaseModelSerializer
class SurgeonSerializer(BaseModelSerializer):
    class Meta:
        model = Surgeon
        fields='__all__'