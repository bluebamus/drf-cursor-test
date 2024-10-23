import pytest
from .factories import AuthorFactory, BookFactory
from django.utils import timezone

@pytest.mark.django_db
class TestAuthorModel:
    def test_author_creation(self):
        author = AuthorFactory()
        assert author.name
        assert not author.deleted

    def test_author_str(self):
        author = AuthorFactory()
        assert str(author) == author.name

@pytest.mark.django_db
class TestBookModel:
    def test_book_creation(self):
        book = BookFactory()
        assert book.title
        assert book.author
        assert not book.deleted

    def test_book_str(self):
        book = BookFactory()
        assert str(book) == book.title

    def test_is_new_release(self):
        book = BookFactory(publication_date=timezone.now().date())
        assert book.is_new_release

    def test_author_name(self):
        book = BookFactory()
        assert book.author_name == book.author.name
