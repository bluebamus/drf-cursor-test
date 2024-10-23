import pytest
from .factories import StudyFactory
from django.utils import timezone

@pytest.mark.django_db
class TestStudyModel:
    def test_study_creation(self):
        study = StudyFactory()
        assert study.title
        assert study.owner
        assert not study.deleted

    def test_study_str(self):
        study = StudyFactory()
        assert str(study) == study.title

    def test_is_active(self):
        study = StudyFactory(start_date=timezone.now().date(), end_date=timezone.now().date() + timezone.timedelta(days=7))
        assert study.is_active

    def test_duration(self):
        study = StudyFactory(start_date=timezone.now().date(), end_date=timezone.now().date() + timezone.timedelta(days=7))
        assert study.duration == 7
