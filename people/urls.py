from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PersonViewSet

# 라우터 사용
router = DefaultRouter()
router.register(r'people', PersonViewSet, basename='person')

urlpatterns = [
    path('', include(router.urls)),
]

# 라우터 미사용 (주석 처리)
# urlpatterns = [
#     path('people/', PersonViewSet.as_view({'get': 'list', 'post': 'create'}), name='person-list'),
#     path('people/<int:pk>/', PersonViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='person-detail'),
#     path('people/<int:pk>/full_name/', PersonViewSet.as_view({'get': 'full_name'}), name='person-full-name'),
#     path('people/adults/', PersonViewSet.as_view({'get': 'adults'}), name='person-adults'),
# ]
