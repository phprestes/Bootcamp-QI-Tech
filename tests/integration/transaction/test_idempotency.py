from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator


class TestIdempotency:
    def test_repeated_request_control_key_returns_same_transaction(self):
        """RN18: o retry com a mesma chave devolve a transação original e não debita de novo."""
        origin = ObjectGenerator.create_account_with_balance(100000)
        destination = ObjectGenerator.create_account()
        payload = PayloadGenerator.create_transfer_payload(destination["account_key"], amount=20000)

        first_status, first = RequestGenerator.POST_transaction(origin["account_key"], payload)
        retry_status, retry = RequestGenerator.POST_transaction(origin["account_key"], payload)

        assert first_status == 201
        assert retry_status == 200
        assert retry == first
        assert ObjectGenerator.get_balance(origin["account_key"]) == 79800
        assert ObjectGenerator.get_balance(destination["account_key"]) == 20000

    def test_repeated_deposit_is_credited_once(self):
        account = ObjectGenerator.create_account()
        payload = PayloadGenerator.create_deposit_payload(amount=5000)

        RequestGenerator.POST_transaction(account["account_key"], payload)
        status, _ = RequestGenerator.POST_transaction(account["account_key"], payload)

        assert status == 200
        assert ObjectGenerator.get_balance(account["account_key"]) == 5000

    def test_reused_request_control_key_with_other_amount_returns_409(self):
        """RN19: mesma chave com corpo diferente é conflito, não repetição."""
        account = ObjectGenerator.create_account()
        payload = PayloadGenerator.create_deposit_payload(amount=5000)
        RequestGenerator.POST_transaction(account["account_key"], payload)

        status, response = RequestGenerator.POST_transaction(
            account["account_key"], {**payload, "amount": 9999}
        )

        assert status == 409
        assert response["code"] == "QIT002016"
        assert ObjectGenerator.get_balance(account["account_key"]) == 5000

    def test_reused_request_control_key_on_other_account_returns_409(self):
        first_account = ObjectGenerator.create_account()
        second_account = ObjectGenerator.create_account()
        payload = PayloadGenerator.create_deposit_payload(amount=5000)
        RequestGenerator.POST_transaction(first_account["account_key"], payload)

        status, response = RequestGenerator.POST_transaction(second_account["account_key"], payload)

        assert status == 409
        assert response["code"] == "QIT002016"
        assert ObjectGenerator.get_balance(second_account["account_key"]) == 0
