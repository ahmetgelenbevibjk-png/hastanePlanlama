from rest_framework.routers import DefaultRouter
from .views import SurgeonViewSet

router = DefaultRouter()
router.register(r'surgeons', SurgeonViewSet, basename='surgeon')

urlpatterns = router.urls