from django.db import models
from django.utils import timezone
from user.models import CustomUser

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)

    def all_with_deleted(self):
        return super().get_queryset()

    def deleted_only(self):
        return super().get_queryset().filter(deleted=True)

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super().delete()

class Study(BaseModel):
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='studies')

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Study'
        verbose_name_plural = 'Studies'

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        return self.start_date <= timezone.now().date() <= self.end_date

    @property
    def duration(self):
        return (self.end_date - self.start_date).days
