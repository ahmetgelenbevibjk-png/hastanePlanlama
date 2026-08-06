from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.auth_views import register_view, login_view

from api.views.schedule_views import RunSchedulerView
from api.views import (
    AnesthesiaTeamViewSet,
    RoomViewSet,
    SurgeonViewSet,
    PatientOperationViewSet,
)

# Router tanımlamaları
router = DefaultRouter()
router.register(r'anesthesias', AnesthesiaTeamViewSet, basename='anesthesia')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'surgeons', SurgeonViewSet, basename='surgeon')
router.register(r'patient-operations', PatientOperationViewSet, basename='patient-operation')

urlpatterns = [
    path('schedule/run/', RunSchedulerView.as_view(), name='run-scheduler'),

    path('', include(router.urls)),
path('auth/register/', register_view, name='register'),
    path('auth/login/', login_view, name='login'),
    ]