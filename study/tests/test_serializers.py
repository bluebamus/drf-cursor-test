import pytest
from .factories import StudyFactory
from study.serializers import StudySerializer

@pytest.mark.django_db
class TestStudySerializer:
    def test_study_serializer(self):
        study = StudyFactory()
        serializer = StudySerializer(study)
        assert serializer.data['title'] == study.title
        assert serializer.data['owner'] == study.owner.username
        assert 'is_active' in serializer.data
        assert 'duration' in serializer.data
