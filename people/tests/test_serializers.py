import pytest
from .factories import PersonFactory
from people.serializers import PersonSerializer

@pytest.mark.django_db
class TestPersonSerializer:
    def test_person_serializer(self):
        person = PersonFactory()
        serializer = PersonSerializer(person)
        assert serializer.data['first_name'] == person.first_name
        assert serializer.data['last_name'] == person.last_name
        assert 'full_name' in serializer.data
        assert 'age' in serializer.data
