import factory
from faker import Faker
from lab.models import Experiment
from user.models import CustomUser

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'password123')

class ExperimentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Experiment

    name = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text')
    start_date = factory.Faker('date_time_this_year')
    end_date = factory.Faker('date_time_this_year')
    status = factory.Faker('random_element', elements=['PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'])
    researcher = factory.SubFactory(UserFactory)
