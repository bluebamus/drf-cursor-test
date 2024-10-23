import pytest
from .factories import ExperimentFactory
from django.utils import timezone

@pytest.mark.django_db
class TestExperimentModel:
    def test_experiment_creation(self):
        experiment = ExperimentFactory()
        assert experiment.name
        assert experiment.researcher
        assert not experiment.deleted

    def test_experiment_str(self):
        experiment = ExperimentFactory()
        assert str(experiment) == experiment.name

    def test_is_active(self):
        experiment = ExperimentFactory(status='IN_PROGRESS')
        assert experiment.is_active

    def test_duration(self):
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(hours=5)
        experiment = ExperimentFactory(start_date=start_date, end_date=end_date)
        assert experiment.duration == 5.0
