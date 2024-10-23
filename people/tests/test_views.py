import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .factories import PersonFactory
from user.tests.factories import UserFactory
from django.utils import timezone

@pytest.mark.django_db
class TestPersonViews:
    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_person_list(self):
        PersonFactory.create_batch(5)
        url = reverse('person-list')
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.data['results']) == 5

    def test_person_create(self):
        person_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'birth_date': '1990-01-01',
            'gender': 'MALE',
        }
        url = reverse('person-list')
        response = self.client.post(url, person_data, format='json')
        assert response.status_code == 201
        assert response.data['first_name'] == 'John'

    def test_person_detail(self):
        person = PersonFactory()
        url = reverse('person-detail', kwargs={'pk': person.pk})
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data['first_name'] == person.first_name

    def test_person_update(self):
        person = PersonFactory()
        url = reverse('person-detail', kwargs={'pk': person.pk})
        update_data = {'first_name': 'Jane'}
        response = self.client.patch(url, update_data, format='json')
        assert response.status_code == 200
        assert response.data['first_name'] == 'Jane'

    def test_person_delete(self):
        person = PersonFactory()
        url = reverse('person-detail', kwargs={'pk': person.pk})
        response = self.client.delete(url)
        assert response.status_code == 204

    def test_adults(self):
        PersonFactory.create_batch(3, birth_date='1990-01-01')
        PersonFactory.create_batch(2, birth_date='2010-01-01')
        url = reverse('person-adults')
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 3

    def test_person_filter_by_gender(self, client):
        PersonFactory(gender='MALE')
        PersonFactory(gender='FEMALE')
        url = reverse('person-list')
        response = client.get(url, {'gender': 'MALE'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['gender'] == 'MALE'

    def test_person_search(self, client):
        PersonFactory(first_name="John", last_name="Doe")
        PersonFactory(first_name="Jane", last_name="Doe")
        url = reverse('person-list')
        response = client.get(url, {'search': 'John'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['first_name'] == "John"

    def test_person_ordering(self, client):
        PersonFactory(first_name="Alice")
        PersonFactory(first_name="Bob")
        url = reverse('person-list')
        response = client.get(url, {'ordering': '-first_name'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['first_name'] == "Bob"

    def test_person_age_calculation(self, client):
        person = PersonFactory(birth_date=timezone.now().date() - timezone.timedelta(days=365*25))
        url = reverse('person-detail', kwargs={'pk': person.pk})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['age'] == 25

    def test_person_zodiac_sign(self, client):
        person = PersonFactory(birth_date=timezone.datetime(2000, 3, 21).date())  # Aries
        url = reverse('person-detail', kwargs={'pk': person.pk})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['zodiac_sign'] == "Aries"
