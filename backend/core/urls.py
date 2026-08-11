from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/anesthesia/', include('anesthesia.urls')),
    path('api/base/', include('base.urls')),
    path('api/patient-operation/', include('patient_operation.urls')),
    path('api/room/', include('room.urls')),
    path('api/surgeon/', include('surgeon.urls')),
    path('api/algorithm/', include('algorithm.urls')),
    path('api/operations/', include('patient_operation.urls')),
]

