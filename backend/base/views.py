from rest_framework import viewsets,permissions
from rest_framework.filters import SearchFilter,OrderingFilter

class BaseViewSet(viewsets.ModelViewSet):
    permissions_classes= [permissions.IsAuthenticated]
    filter_backends=[SearchFilter,OrderingFilter]