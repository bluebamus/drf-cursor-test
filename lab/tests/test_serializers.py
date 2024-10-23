import pytest
from .factories import ExperimentFactory
from lab.serializers import ExperimentSerializer

@pytest.mark.django_db
class TestExperimentSerializer:
    def test_experiment_serializer(self):
        experiment = ExperimentFactory()
        serializer = ExperimentSerializer(experiment)
        assert serializer.data['name'] == experiment.name
        assert serializer.data['researcher'] == experiment.researcher.username
        assert 'is_active' in serializer.data
        assert 'duration' in serializer.data
