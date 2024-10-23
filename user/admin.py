from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils import timezone

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('deleted',)
    list_filter = UserAdmin.list_filter + ('deleted',)
    actions = ['soft_delete', 'restore']

    # 소프트 삭제 액션
    def soft_delete(self, request, queryset):
        queryset.update(deleted=True, deleted_at=timezone.now())
    soft_delete.short_description = "Soft delete selected users"

    # 삭제 취소 액션
    def restore(self, request, queryset):
        queryset.update(deleted=False, deleted_at=None)
    restore.short_description = "Restore selected users"
