from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

def validate_experiment_duration(start_date, end_date):
    duration = (end_date - start_date).total_seconds() / 3600  # duration in hours
    if duration < 1 or duration > 168:  # 1 hour to 1 week
        raise ValidationError(
            _('Experiment duration must be between 1 hour and 1 week.'),
        )

def validate_experiment_status_change(old_status, new_status):
    valid_transitions = {
        'PLANNED': ['IN_PROGRESS', 'CANCELLED'],
        'IN_PROGRESS': ['COMPLETED', 'CANCELLED'],
        'COMPLETED': [],
        'CANCELLED': [],
    }
    if new_status not in valid_transitions.get(old_status, []):
        raise ValidationError(
            _(f'Invalid status transition from {old_status} to {new_status}.'),
        )
