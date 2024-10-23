from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'profile_image', 'deleted')
        read_only_fields = ('deleted',)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # 비밀번호는 쓰기 전용

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')

    # 사용자 생성 메서드
    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'profile_image')  # 수정 가능한 필드
