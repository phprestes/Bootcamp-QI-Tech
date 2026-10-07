from tests.utils.mock_generator import BureauMock
from tests.utils.payload_generator import PayloadGenerator
from tests.utils.request_generator import RequestGenerator


class ObjectGenerator:
    """Cria entidades prontas pela API (porta da frente), nunca pelo banco."""

    @staticmethod
    def create_customer(**overrides) -> dict:
        payload = PayloadGenerator.create_customer_payload(**overrides)
        BureauMock.regular(payload["document_number"])

        status, response = RequestGenerator.POST_customer(payload)
        assert status == 201, response

        return {**response, **payload}

    @staticmethod
    def create_account(customer_key: str = None) -> dict:
        if customer_key is None:
            customer_key = ObjectGenerator.create_customer()["customer_key"]

        status, response = RequestGenerator.POST_account(customer_key)
        assert status == 201, response

        return {**response, "customer_key": customer_key}

    @staticmethod
    def deposit(account_key: str, amount: int) -> dict:
        status, response = RequestGenerator.POST_transaction(
            account_key, PayloadGenerator.create_deposit_payload(amount)
        )
        assert status == 201, response

        return response

    @staticmethod
    def create_account_with_balance(amount: int) -> dict:
        account = ObjectGenerator.create_account()
        if amount > 0:
            ObjectGenerator.deposit(account["account_key"], amount)

        return account

    @staticmethod
    def get_balance(account_key: str) -> int:
        status, response = RequestGenerator.GET_account(account_key)
        assert status == 200, response

        return response["balance"]
