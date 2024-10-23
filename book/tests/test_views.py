import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from .factories import UserFactory, AuthorFactory, BookFactory
from book.models import Book

@pytest.mark.django_db
class TestBookViews:
    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_book_list(self):
        BookFactory.create_batch(5)
        url = reverse('book-list')
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.data['results']) == 5

    def test_book_create(self):
        author = AuthorFactory()
        book_data = {
            'title': 'New Book',
            'author': {'name': author.name},
            'publication_date': '2023-01-01',
            'isbn': '1234567890123',
            'price': '29.99',
            'pages': 200,
            'rating': 4.5,
            'description': 'A great book'
        }
        url = reverse('book-list')
        response = self.client.post(url, book_data, format='json')
        assert response.status_code == 201
        assert response.data['title'] == 'New Book'

    def test_book_detail(self):
        book = BookFactory()
        url = reverse('book-detail', kwargs={'pk': book.pk})
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data['title'] == book.title

    def test_book_update(self):
        book = BookFactory()
        url = reverse('book-detail', kwargs={'pk': book.pk})
        update_data = {'title': 'Updated Title'}
        response = self.client.patch(url, update_data, format='json')
        assert response.status_code == 200
        assert response.data['title'] == 'Updated Title'

    def test_book_delete(self):
        book = BookFactory()
        url = reverse('book-detail', kwargs={'pk': book.pk})
        response = self.client.delete(url)
        assert response.status_code == 204

    def test_popular_books(self):
        BookFactory.create_batch(3, rating=4.5)
        BookFactory.create_batch(2, rating=3.5)
        url = reverse('book-popular')
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 3

    def test_book_filter_by_author(self):
        author = AuthorFactory()
        BookFactory.create_batch(3, author=author)
        BookFactory.create_batch(2)  # 다른 저자의 책
        url = reverse('book-list')
        response = self.client.get(url, {'author': author.id})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_book_search(self):
        BookFactory(title="Python Programming")
        BookFactory(title="Java Programming")
        url = reverse('book-list')
        response = self.client.get(url, {'search': 'Python'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == "Python Programming"

    def test_book_ordering(self):
        BookFactory(title="A Book", price=10.00)
        BookFactory(title="B Book", price=20.00)
        url = reverse('book-list')
        response = self.client.get(url, {'ordering': '-price'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['title'] == "B Book"

    @pytest.mark.parametrize('price, expected_count', [
        (15, 1),  # 15달러 이상의 책 1권
        (5, 2),   # 5달러 이상의 책 2권
    ])
    def test_book_filter_by_price(self, client, price, expected_count):
        BookFactory(price=10.00)
        BookFactory(price=20.00)
        url = reverse('book-list')
        response = client.get(url, {'min_price': price})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == expected_count

    def test_new_release_property(self, client):
        book = BookFactory(publication_date=timezone.now().date())
        url = reverse('book-detail', kwargs={'pk': book.pk})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_new_release'] == True

