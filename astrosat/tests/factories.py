import factory
from factory.faker import Faker as FactoryFaker
from faker import Faker
from typing import Any, Sequence

from django.contrib.auth import get_user_model

from astrosat.models import DatabaseLogTag, DatabaseLogRecord

fake = Faker()

#########
# users #
#########


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ["username"]

    username = FactoryFaker("user_name")
    email = FactoryFaker("email")

    @factory.post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):

        password_kwargs = {
            "length": 42,
            "special_chars": True,
            "digits": True,
            "upper_case": True,
            "lower_case": True,
        }
        password = fake.password(**password_kwargs)
        self.set_password(password)


########
# logs #
########


class DatabaseLogTagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DatabaseLogTag

    name = factory.LazyAttributeSequence(lambda o, n: f"tag-{n}")


class DatabaseLogRecordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DatabaseLogRecord

    logger_name = "db"
    level = FactoryFaker(
        "random_element",
        elements=[x[0] for x in DatabaseLogRecord.LevelChoices]
    )
    message = FactoryFaker("sentence", nb_words=10)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for tag in tags:
                self.tags.add(tag)
