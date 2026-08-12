from django.urls import path
from .views import RunOptimizationAPIView

urlpatterns = [
    path('run/', RunOptimizationAPIView.as_view(), name='run-optimization'),
]