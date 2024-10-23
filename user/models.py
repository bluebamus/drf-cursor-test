from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    deleted = models.BooleanField(default=False)  # 소프트 삭제를 위한 필드
    deleted_at = models.DateTimeField(null=True, blank=True)  # 삭제 시간 기록

    # 소프트 삭제 메서드
    def soft_delete(self):
        self.deleted = True
        self.deleted_at = timezone.now()
        self.save()

    # 삭제 취소 메서드
    def restore(self):
        self.deleted = False
        self.deleted_at = None
        self.save()
