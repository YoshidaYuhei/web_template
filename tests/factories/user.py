from datetime import date, datetime, timezone

import factory

from app.models.user import Gender, User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Faker("uuid4")
    account_id = factory.LazyAttribute(
        lambda o: o.account.id if hasattr(o, "account") else None
    )
    nickname = factory.Sequence(lambda n: f"user{n}")
    gender = Gender.MALE
    birth_date = date(1990, 1, 1)
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
