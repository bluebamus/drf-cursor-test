from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
import datetime

def validate_future_date(value):
    if value < datetime.date.today():
        raise ValidationError(
            _('%(value)s is in the past. Publication date must be in the future.'),
            params={'value': value},
        )

def validate_isbn(value):
    if not value.isdigit() or len(value) != 13:
        raise ValidationError(
            _('%(value)s is not a valid ISBN. It must be a 13-digit number.'),
            params={'value': value},
        )

title_validator = RegexValidator(
    regex=r'^[A-Za-z0-9\s\-_,\.;:()]+$',
    message="Title must contain only letters, numbers, spaces, and basic punctuation.",
)

price_validator = MinValueValidator(0.01, message="Price must be greater than 0.")

rating_validator = MaxValueValidator(5.0, message="Rating must not exceed 5.0.")

class YearValidator:
    def __init__(self, start_year, end_year):
        self.start_year = start_year
        self.end_year = end_year

    def __call__(self, value):
        if value.year < self.start_year or value.year > self.end_year:
            raise ValidationError(
                _(f'Year must be between {self.start_year} and {self.end_year}.'),
                params={'value': value},
            )
