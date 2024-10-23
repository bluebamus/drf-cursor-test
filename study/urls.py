from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudyViewSet

router = DefaultRouter()
router.register(r'studies', StudyViewSet, basename='study')

urlpatterns = [
    path('', include(router.urls)),
]
