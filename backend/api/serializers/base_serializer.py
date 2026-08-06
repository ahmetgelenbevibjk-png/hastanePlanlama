from rest_framework import serializers

class BaseModelSerializer(serializers.Serializer):
    """
    Tüm ModelSerializer'ların türeyeceği temel serializer sınıfı.
    """
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S", required=False)
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S", required=False)