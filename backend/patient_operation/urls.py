from rest_framework.routers import DefaultRouter
from .views import PatientOperationViewSet

router = DefaultRouter()
router.register(r'patient-operations', PatientOperationViewSet, basename='patientoperation')

urlpatterns = router.urls