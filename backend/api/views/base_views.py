from rest_framework import viewsets,permissions,filters

class BaseViewSet(viewsets.ModelViewSet):
    permission_classes=[permissions.IsAuthenticated]
    filter_backends=[filters.SearchFilter,filters.OrderingFilter]
