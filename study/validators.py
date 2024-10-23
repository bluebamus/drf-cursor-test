from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

def validate_date_not_in_past(value):
    if value < timezone.now().date():
        raise ValidationError(
            _('%(value)s is in the past. Start date must be in the future or today.'),
            params={'value': value},
        )

def validate_end_date_after_start_date(start_date, end_date):
    if end_date <= start_date:
        raise ValidationError(
            _('End date must be after start date.'),
        )

def validate_study_duration(start_date, end_date):
    duration = (end_date - start_date).days
    if duration < 7 or duration > 365:
        raise ValidationError(
            _('Study duration must be between 1 week and 1 year.'),
        )
