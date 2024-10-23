import factory
from faker import Faker
from book.models import Author, Book
from user.models import CustomUser

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'password123')

class AuthorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Author

    name = factory.Faker('name')
    bio = factory.Faker('text')

class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    title = factory.Faker('sentence', nb_words=4)
    author = factory.SubFactory(AuthorFactory)
    publication_date = factory.Faker('date_this_decade')
    isbn = factory.Faker('isbn13')
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    pages = factory.Faker('random_int', min=50, max=1000)
    rating = factory.Faker('pyfloat', left_digits=1, right_digits=1, min_value=0, max_value=5)
    description = factory.Faker('text')
