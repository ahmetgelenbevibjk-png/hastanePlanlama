from django.urls import path
from .views import ScheduleOptimizeView, ManualScheduleUpdateView

urlpatterns = [
    path('run/', ScheduleOptimizeView.as_view(), name='algorithm-run'),
    path('optimize/', ScheduleOptimizeView.as_view(), name='schedule-optimize'),
    path('manual-update/', ManualScheduleUpdateView.as_view(), name='manual-schedule-update'),
]