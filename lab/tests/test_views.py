import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from .factories import UserFactory, ExperimentFactory

@pytest.mark.django_db
class TestExperimentViews:
    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_experiment_list(self):
        ExperimentFactory.create_batch(5, researcher=self.user)
        url = reverse('experiment-list')
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.data['results']) == 5

    def test_experiment_create(self):
        experiment_data = {
            'name': 'New Experiment',
            'description': 'A new experiment description',
            'start_date': '2023-01-01T00:00:00Z',
            'end_date': '2023-12-31T23:59:59Z',
            'status': 'PLANNED',
        }
        url = reverse('experiment-list')
        response = self.client.post(url, experiment_data, format='json')
        assert response.status_code == 201
        assert response.data['name'] == 'New Experiment'

    def test_experiment_detail(self):
        experiment = ExperimentFactory(researcher=self.user)
        url = reverse('experiment-detail', kwargs={'pk': experiment.pk})
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data['name'] == experiment.name

    def test_experiment_update(self):
        experiment = ExperimentFactory(researcher=self.user)
        url = reverse('experiment-detail', kwargs={'pk': experiment.pk})
        update_data = {'name': 'Updated Name'}
        response = self.client.patch(url, update_data, format='json')
        assert response.status_code == 200
        assert response.data['name'] == 'Updated Name'

    def test_experiment_delete(self):
        experiment = ExperimentFactory(researcher=self.user)
        url = reverse('experiment-detail', kwargs={'pk': experiment.pk})
        response = self.client.delete(url)
        assert response.status_code == 204

    def test_experiments_by_status(self):
        ExperimentFactory.create_batch(3, researcher=self.user, status='IN_PROGRESS')
        ExperimentFactory.create_batch(2, researcher=self.user, status='COMPLETED')
        url = reverse('experiment-by-status')
        response = self.client.get(url, {'status': 'IN_PROGRESS'})
        assert response.status_code == 200
        assert len(response.data) == 3

    def test_experiment_filter_by_status(self, client):
        ExperimentFactory(status='PLANNED')
        ExperimentFactory(status='IN_PROGRESS')
        url = reverse('experiment-list')
        response = client.get(url, {'status': 'PLANNED'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['status'] == 'PLANNED'

    def test_experiment_search(self, client):
        ExperimentFactory(name="Physics Experiment")
        ExperimentFactory(name="Chemistry Experiment")
        url = reverse('experiment-list')
        response = client.get(url, {'search': 'Physics'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == "Physics Experiment"

    def test_experiment_ordering(self, client):
        ExperimentFactory(name="A Experiment", start_date=timezone.now())
        ExperimentFactory(name="B Experiment", start_date=timezone.now() + timezone.timedelta(hours=1))
        url = reverse('experiment-list')
        response = client.get(url, {'ordering': '-start_date'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['name'] == "B Experiment"

    def test_experiment_duration_calculation(self, client):
        experiment = ExperimentFactory(
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(hours=5)
        )
        url = reverse('experiment-detail', kwargs={'pk': experiment.pk})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['duration'] == 5.0

