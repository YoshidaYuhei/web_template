import pytest
from sqlalchemy.exc import IntegrityError

from app.models.account import Account
from app.models.account_passkey import AccountPasskey


@pytest.mark.asyncio
class TestAccountPasskey:
    async def test_create_account_passkey(self, test_session_factory):
        async with test_session_factory() as session:
            account = Account(email="passkey@example.com")
            session.add(account)
            await session.commit()
            await session.refresh(account)

            passkey = AccountPasskey(
                account_id=account.id,
                credential_id="cred_abc",
                public_key="pk_xyz",
            )
            session.add(passkey)
            await session.commit()
            await session.refresh(passkey)

            assert passkey.id is not None
            assert passkey.credential_id == "cred_abc"
            assert passkey.public_key == "pk_xyz"

            await session.delete(passkey)
            await session.delete(account)
            await session.commit()

    async def test_multiple_passkeys(self, test_session_factory):
        async with test_session_factory() as session:
            account = Account(email="multi_pk@example.com")
            session.add(account)
            await session.commit()
            await session.refresh(account)

            pk1 = AccountPasskey(
                account_id=account.id,
                credential_id="cred_1",
                public_key="pk_1",
            )
            pk2 = AccountPasskey(
                account_id=account.id,
                credential_id="cred_2",
                public_key="pk_2",
            )
            session.add_all([pk1, pk2])
            await session.commit()

            await session.refresh(pk1)
            await session.refresh(pk2)
            assert pk1.id is not None
            assert pk2.id is not None

            await session.delete(pk1)
            await session.delete(pk2)
            await session.delete(account)
            await session.commit()

    async def test_credential_id_unique_constraint(self, test_session_factory):
        async with test_session_factory() as session:
            account1 = Account(email="pk_dup1@example.com")
            account2 = Account(email="pk_dup2@example.com")
            session.add_all([account1, account2])
            await session.commit()
            await session.refresh(account1)
            await session.refresh(account2)

            pk1 = AccountPasskey(
                account_id=account1.id,
                credential_id="dup_cred",
                public_key="pk_a",
            )
            session.add(pk1)
            await session.commit()

            pk2 = AccountPasskey(
                account_id=account2.id,
                credential_id="dup_cred",
                public_key="pk_b",
            )
            session.add(pk2)
            pk1_id = pk1.id
            account1_id = account1.id
            account2_id = account2.id

            with pytest.raises(IntegrityError):
                await session.commit()
            await session.rollback()

            result = await session.get(AccountPasskey, pk1_id)
            if result:
                await session.delete(result)
            for acc_id in [account1_id, account2_id]:
                a = await session.get(Account, acc_id)
                if a:
                    await session.delete(a)
            await session.commit()

    async def test_sign_count_default_zero(self, test_session_factory):
        async with test_session_factory() as session:
            account = Account(email="pk_sc@example.com")
            session.add(account)
            await session.commit()
            await session.refresh(account)

            passkey = AccountPasskey(
                account_id=account.id,
                credential_id="cred_sc",
                public_key="pk_sc",
            )
            session.add(passkey)
            await session.commit()
            await session.refresh(passkey)

            assert passkey.sign_count == 0

            await session.delete(passkey)
            await session.delete(account)
            await session.commit()
