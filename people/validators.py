from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator, RegexValidator
import datetime

def validate_adult(birth_date):
    today = datetime.date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    if age < 18:
        raise ValidationError(
            _('Person must be at least 18 years old.'),
        )

name_validator = RegexValidator(
    regex=r'^[A-Za-z\s\-]+$',
    message="Name must contain only letters, spaces, and hyphens.",
)

custom_email_validator = EmailValidator(message="Enter a valid email address.")

def validate_gender(value):
    valid_genders = ['MALE', 'FEMALE', 'OTHER']
    if value not in valid_genders:
        raise ValidationError(
            _(f'{value} is not a valid gender. Choose from {", ".join(valid_genders)}.'),
        )
