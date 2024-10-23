from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from .models import Author, Book
import csv

class BookInline(admin.TabularInline):
    model = Book
    extra = 0

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at', 'deleted')
    list_filter = ('deleted', 'created_at')
    search_fields = ('name',)
    inlines = [BookInline]
    actions = ['soft_delete', 'hard_delete', 'undelete', 'export_as_csv']

    # 소프트 삭제 액션
    def soft_delete(self, request, queryset):
        queryset.update(deleted=True, deleted_at=timezone.now())
    soft_delete.short_description = "Soft delete selected authors"

    # 하드 삭제 액션
    def hard_delete(self, request, queryset):
        queryset.delete()
    hard_delete.short_description = "Permanently delete selected authors"

    # 삭제 취소 액션
    def undelete(self, request, queryset):
        queryset.update(deleted=False, deleted_at=None)
    undelete.short_description = "Undelete selected authors"

    # CSV 내보내기 액션
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response
    export_as_csv.short_description = "Export selected authors as CSV"

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_date', 'price', 'rating', 'created_at', 'updated_at', 'deleted')
    list_filter = ('author', 'publication_date', 'deleted', 'created_at')
    search_fields = ('title', 'author__name', 'isbn')
    date_hierarchy = 'publication_date'
    actions = ['soft_delete', 'hard_delete', 'undelete', 'export_as_csv', 'duplicate_books']

    # 소프트 삭제 액션
    def soft_delete(self, request, queryset):
        queryset.update(deleted=True, deleted_at=timezone.now())
    soft_delete.short_description = "Soft delete selected books"

    # 하드 삭제 액션
    def hard_delete(self, request, queryset):
        queryset.delete()
    hard_delete.short_description = "Permanently delete selected books"

    # 삭제 취소 액션
    def undelete(self, request, queryset):
        queryset.update(deleted=False, deleted_at=None)
    undelete.short_description = "Undelete selected books"

    # CSV 내보내기 액션
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response
    export_as_csv.short_description = "Export selected books as CSV"

    # 책 복제 액션
    def duplicate_books(self, request, queryset):
        for book in queryset:
            book.pk = None
            book.title = f"Copy of {book.title}"
            book.slug = None  # 자동 생성됨
            book.save()
    duplicate_books.short_description = "Duplicate selected books"
