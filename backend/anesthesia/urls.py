from rest_framework.routers import DefaultRouter
from .views import AnesthesiaTeamViewSet

router = DefaultRouter()
router.register(r'anesthesia-teams', AnesthesiaTeamViewSet, basename='anesthesiateam')

urlpatterns = router.urls
