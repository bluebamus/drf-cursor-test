import pytest
from .factories import AuthorFactory, BookFactory
from book.serializers import AuthorSerializer, BookSerializer

@pytest.mark.django_db
class TestAuthorSerializer:
    def test_author_serializer(self):
        author = AuthorFactory()
        serializer = AuthorSerializer(author)
        assert serializer.data['name'] == author.name
        assert 'bio' in serializer.data

@pytest.mark.django_db
class TestBookSerializer:
    def test_book_serializer(self):
        book = BookFactory()
        serializer = BookSerializer(book)
        assert serializer.data['title'] == book.title
        assert serializer.data['author']['name'] == book.author.name
        assert 'is_new_release' in serializer.data
        assert 'author_name' in serializer.data
