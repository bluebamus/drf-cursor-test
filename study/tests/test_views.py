import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from .factories import UserFactory, StudyFactory

@pytest.mark.django_db
class TestStudyViews:
    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_study_list(self):
        StudyFactory.create_batch(5, owner=self.user)
        url = reverse('study-list')
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.data['results']) == 5

    def test_study_create(self):
        study_data = {
            'title': 'New Study',
            'description': 'A new study description',
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
        }
        url = reverse('study-list')
        response = self.client.post(url, study_data, format='json')
        assert response.status_code == 201
        assert response.data['title'] == 'New Study'

    def test_study_detail(self):
        study = StudyFactory(owner=self.user)
        url = reverse('study-detail', kwargs={'pk': study.pk})
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data['title'] == study.title

    def test_study_update(self):
        study = StudyFactory(owner=self.user)
        url = reverse('study-detail', kwargs={'pk': study.pk})
        update_data = {'title': 'Updated Title'}
        response = self.client.patch(url, update_data, format='json')
        assert response.status_code == 200
        assert response.data['title'] == 'Updated Title'

    def test_study_delete(self):
        study = StudyFactory(owner=self.user)
        url = reverse('study-detail', kwargs={'pk': study.pk})
        response = self.client.delete(url)
        assert response.status_code == 204

    def test_active_studies(self):
        StudyFactory.create_batch(3, owner=self.user, start_date='2023-01-01', end_date='2023-12-31')
        StudyFactory.create_batch(2, owner=self.user, start_date='2022-01-01', end_date='2022-12-31')
        url = reverse('study-active')
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 3

    def test_study_filter_by_date_range(self):
        StudyFactory(start_date=timezone.now().date(), end_date=timezone.now().date() + timezone.timedelta(days=10))
        StudyFactory(start_date=timezone.now().date() + timezone.timedelta(days=20), end_date=timezone.now().date() + timezone.timedelta(days=30))
        url = reverse('study-list')
        response = self.client.get(url, {'start_date_after': timezone.now().date(), 'end_date_before': timezone.now().date() + timezone.timedelta(days=15)})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_study_search(self):
        StudyFactory(title="Python Study Group")
        StudyFactory(title="Java Study Group")
        url = reverse('study-list')
        response = self.client.get(url, {'search': 'Python'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == "Python Study Group"

    def test_study_ordering(self):
        StudyFactory(title="A Study", start_date=timezone.now().date())
        StudyFactory(title="B Study", start_date=timezone.now().date() + timezone.timedelta(days=1))
        url = reverse('study-list')
        response = self.client.get(url, {'ordering': '-start_date'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['title'] == "B Study"

    def test_study_by_duration(self):
        StudyFactory(start_date=timezone.now().date(), end_date=timezone.now().date() + timezone.timedelta(days=5))
        StudyFactory(start_date=timezone.now().date(), end_date=timezone.now().date() + timezone.timedelta(days=15))
        url = reverse('study-by-duration')
        response = self.client.get(url, {'min_duration': 10, 'max_duration': 20})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

