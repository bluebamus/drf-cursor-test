from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, complex_book_analysis

router = DefaultRouter()
router.register(r'books', BookViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('complex-analysis/', complex_book_analysis, name='complex_book_analysis'),
]
