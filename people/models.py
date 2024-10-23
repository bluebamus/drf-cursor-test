from django.db import models
from django.utils import timezone

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

class Person(BaseModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=[
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other')
    ])

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Person'
        verbose_name_plural = 'People'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
