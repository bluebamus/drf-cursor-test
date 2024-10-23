import pytest
from django.urls import reverse
from rest_framework import status
from .factories import CustomUserFactory
from django.utils import timezone

@pytest.mark.django_db
class TestCustomUserViewSet:
    def test_user_registration(self, client):
        url = reverse('customuser-list')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpass123'
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data

    def test_user_login(self, client):
        user = CustomUserFactory(username='testuser')
        user.set_password('testpass123')
        user.save()
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_user_profile_update(self, client):
        user = CustomUserFactory()
        client.force_authenticate(user=user)
        url = reverse('customuser-detail', kwargs={'pk': user.pk})
        data = {
            'email': 'newemail@example.com'
        }
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'newemail@example.com'

    def test_user_soft_delete(self, client):
        user = CustomUserFactory()
        client.force_authenticate(user=user)
        url = reverse('customuser-soft-delete', kwargs={'pk': user.pk})
        response = client.post(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.deleted == True

    def test_user_restore(self, client):
        user = CustomUserFactory(deleted=True, deleted_at=timezone.now())
        client.force_authenticate(user=user)
        url = reverse('customuser-restore', kwargs={'pk': user.pk})
        response = client.post(url)
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.deleted == False
        assert user.deleted_at is None
