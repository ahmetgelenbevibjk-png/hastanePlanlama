from django.urls import path
from .views import ScheduleOptimizeView

urlpatterns = [
    path('run/', ScheduleOptimizeView.as_view(), name='algorithm-run'),
]