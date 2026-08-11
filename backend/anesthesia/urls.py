from rest_framework.routers import DefaultRouter
from .views import AnesthesiaTeamViewSet

router = DefaultRouter()
router.register(r'', AnesthesiaTeamViewSet, basename='anesthesiateam')

urlpatterns = router.urls
