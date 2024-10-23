from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from .validators import validate_future_date, validate_isbn, title_validator, price_validator, rating_validator, YearValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image
import os
from datetime import date
from django.contrib.auth import get_user_model

User = get_user_model()

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    if ext.lower() == '.exe':
        raise ValidationError(_('EXE files are not allowed.'))

def validate_file_size(value):
    if value.size > 500 * 1024 * 1024:
        raise ValidationError(_('File size must be no more than 500MB.'))

def image_upload_path(instance, filename):
    return f'img/{date.today().strftime("%Y/%m/%d")}/{filename}'

class SoftDeleteManager(models.Manager):
    # 삭제되지 않은 객체만 반환하는 커스텀 매니저
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)

    # 모든 객체(삭제된 객체 포함) 반환
    def all_with_deleted(self):
        return super().get_queryset()

    # 삭제된 객체만 반환
    def deleted_only(self):
        return super().get_queryset().filter(deleted=True)

class BaseModel(models.Model):
    # 모든 모델에 공통으로 사용되는 필드들
    created_at = models.DateTimeField(auto_now_add=True)  # 객체 생성 시간
    updated_at = models.DateTimeField(auto_now=True)  # 객체 수정 시간
    deleted_at = models.DateTimeField(null=True, blank=True)  # 객체 삭제 시간
    deleted = models.BooleanField(default=False)  # 삭제 여부

    objects = SoftDeleteManager()  # 커스텀 매니저 사용

    class Meta:
        abstract = True  # 이 모델은 추상 모델로, 실제 테이블로 생성되지 않음

    # 소프트 삭제 구현
    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_at = timezone.now()
        self.save()

    # 실제 데이터베이스에서 삭제
    def hard_delete(self):
        super().delete()

class Author(BaseModel):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Book(BaseModel):
    title = models.CharField(max_length=100, validators=[title_validator])
    slug = models.SlugField(unique=True, blank=True)  # URL에 사용될 슬러그
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    publication_date = models.DateField(validators=[validate_future_date, YearValidator(2000, 2100)])
    isbn = models.CharField(max_length=13, unique=True, validators=[validate_isbn])
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[price_validator])
    pages = models.PositiveIntegerField()
    rating = models.FloatField(default=0.0, validators=[rating_validator])
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to=image_upload_path, blank=True, null=True)
    attachment = models.FileField(upload_to='attachments/', validators=[validate_file_extension, validate_file_size], blank=True, null=True)
    genres = models.ManyToManyField(Genre, related_name='books')
    average_rating = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-publication_date']  # 출판일 기준 내림차순 정렬
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return self.title

    # 저장 시 자동으로 슬러그 생성
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        if self.cover_image:
            img = Image.open(self.cover_image.path)
            if img.height > 500 or img.width > 500:
                output_size = (500, 500)
                img.thumbnail(output_size)
            if img.format != 'PNG':
                img = img.convert('RGB')
            img.save(self.cover_image.path, 'PNG')

    # 새 출시 여부 확인 (30일 이내)
    @property
    def is_new_release(self):
        return (timezone.now().date() - self.publication_date) <= timezone.timedelta(days=30)

    # 저자 이름 반환
    @property
    def author_name(self):
        return self.author.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    favorite_genres = models.ManyToManyField(Genre, related_name='users')
    read_books = models.ManyToManyField(Book, related_name='readers', through='ReadingHistory')

class ReadingHistory(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date_read = models.DateField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])

class BookRecommendation(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='recommendations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
