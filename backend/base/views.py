from rest_framework import viewsets,status
from rest_framework.response import Response

class BaseViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def perform_destroy(self,instance):
        instance.is_active=False
        instance.save()