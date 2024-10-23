import factory
from faker import Faker
from study.models import Study
from user.models import CustomUser

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'password123')

class StudyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Study

    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text')
    start_date = factory.Faker('date_this_year')
    end_date = factory.Faker('date_this_year')
    owner = factory.SubFactory(UserFactory)
