from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CustomUser
from .serializers import CustomUserSerializer, UserRegistrationSerializer, UserUpdateSerializer

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(deleted=False)
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    # 아래 메서드들은 ModelViewSet에서 자동으로 제공되므로 주석 처리합니다.
    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)

    # def create(self, request, *args, **kwargs):
    #     return super().create(request, *args, **kwargs)

    # def retrieve(self, request, *args, **kwargs):
    #     return super().retrieve(request, *args, **kwargs)

    # def update(self, request, *args, **kwargs):
    #     return super().update(request, *args, **kwargs)

    # def destroy(self, request, *args, **kwargs):
    #     return super().destroy(request, *args, **kwargs)

    # 커스텀 액션은 그대로 유지
    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        """
        사용자를 소프트 삭제합니다.
        오버라이딩 이유: 커스텀 소프트 삭제 기능 구현
        """
        user = self.get_object()
        user.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        소프트 삭제된 사용자를 복구합니다.
        오버라이딩 이유: 커스텀 복구 기능 구현
        """
        user = self.get_object()
        user.restore()
        return Response(status=status.HTTP_200_OK)

    # 오버라이딩이 필요한 메서드는 그대로 유지
    def perform_destroy(self, instance):
        """
        사용자를 삭제합니다. (소프트 삭제 수행)
        오버라이딩 이유: 실제 삭제 대신 소프트 삭제 수행
        """
        instance.soft_delete()
