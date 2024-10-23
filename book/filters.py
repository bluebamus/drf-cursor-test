import django_filters
from .models import Book, Author
from django.db.models import Count

class BookFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    publication_year = django_filters.NumberFilter(field_name="publication_date", lookup_expr='year')
    
    class Meta:
        model = Book
        fields = ['author', 'publication_year', 'min_price', 'max_price']

class AuthorFilter(django_filters.FilterSet):
    min_books = django_filters.NumberFilter(method='filter_min_books')
    
    class Meta:
        model = Author
        fields = ['name']
    
    def filter_min_books(self, queryset, name, value):
        return queryset.annotate(book_count=Count('books')).filter(book_count__gte=value)
