import factory
from faker import Faker
from people.models import Person

fake = Faker()

class PersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Person

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    birth_date = factory.Faker('date_of_birth', minimum_age=18, maximum_age=90)
    gender = factory.Faker('random_element', elements=['MALE', 'FEMALE', 'OTHER'])
