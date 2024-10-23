import pytest
from .factories import PersonFactory
from django.utils import timezone

@pytest.mark.django_db
class TestPersonModel:
    def test_person_creation(self):
        person = PersonFactory()
        assert person.first_name
        assert person.last_name
        assert not person.deleted

    def test_person_str(self):
        person = PersonFactory()
        assert str(person) == f"{person.first_name} {person.last_name}"

    def test_full_name(self):
        person = PersonFactory()
        assert person.full_name == f"{person.first_name} {person.last_name}"

    def test_age(self):
        person = PersonFactory(birth_date=timezone.now().date() - timezone.timedelta(days=365*25))
        assert person.age == 25
