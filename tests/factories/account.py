from datetime import datetime, timedelta, timezone

import factory

from app.core.security import create_refresh_token, get_password_hash
from app.models.account import Account


class AccountFactory(factory.Factory):
    class Meta:
        model = Account

    id = factory.Faker("uuid4")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    hashed_password = factory.LazyAttribute(lambda _: get_password_hash("password123"))
    refresh_token = factory.LazyAttribute(lambda _: create_refresh_token()[0])
    refresh_token_expires_at = factory.LazyAttribute(
        lambda _: datetime.now(timezone.utc) + timedelta(days=7)
    )
    is_email_verified = False
    is_active = True
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
