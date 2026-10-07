from tests.utils import ObjectGenerator, PayloadGenerator, RandomGenerator, RequestGenerator


class TestDeposit:
    def test_deposit_on_active_account_returns_201(self):
        """RN12 (caminho que passa): depósito credita e devolve o saldo novo."""
        account = ObjectGenerator.create_account()

        status, response = RequestGenerator.POST_transaction(
            account["account_key"], PayloadGenerator.create_deposit_payload(amount=15050)
        )

        assert status == 201
        assert len(response["transaction_key"]) == 36
        assert response["type"] == "DEPOSIT"
        assert response["amount"] == 15050
        assert response["fee"] == 0
        assert response["balance"] == 15050
        assert ObjectGenerator.get_balance(account["account_key"]) == 15050

    def test_deposit_on_blocked_account_returns_409(self):
        """RN12: conta fora de ACTIVE não movimenta."""
        account = ObjectGenerator.create_account()
        RequestGenerator.PUT_account_status(account["account_key"], {"status": "BLOCKED"})

        status, response = RequestGenerator.POST_transaction(
            account["account_key"], PayloadGenerator.create_deposit_payload()
        )

        assert status == 409
        assert response["code"] == "QIT002009"
        assert ObjectGenerator.get_balance(account["account_key"]) == 0

    def test_deposit_on_closed_account_returns_409(self):
        account = ObjectGenerator.create_account()
        RequestGenerator.PUT_account_status(account["account_key"], {"status": "CLOSED"})

        status, response = RequestGenerator.POST_transaction(
            account["account_key"], PayloadGenerator.create_deposit_payload()
        )

        assert status == 409
        assert response["code"] == "QIT002009"

    def test_deposit_on_unknown_account_returns_404(self):
        status, response = RequestGenerator.POST_transaction(
            RandomGenerator.generate_uuid(), PayloadGenerator.create_deposit_payload()
        )

        assert status == 404
        assert response["code"] == "QIT002007"

    def test_deposit_with_zero_amount_returns_400(self):
        """RN13: valor mínimo de 1 centavo."""
        account = ObjectGenerator.create_account()

        status, response = RequestGenerator.POST_transaction(
            account["account_key"], PayloadGenerator.create_deposit_payload(amount=0)
        )

        assert status == 400
        assert response["code"] == "QIT000001"

    def test_deposit_with_decimal_amount_returns_400(self):
        """R6: dinheiro é inteiro em centavos; 10.5 não é aceito."""
        account = ObjectGenerator.create_account()

        status, response = RequestGenerator.POST_transaction(
            account["account_key"], PayloadGenerator.create_deposit_payload(amount=10.5)
        )

        assert status == 400
        assert response["code"] == "QIT000001"

    def test_deposit_without_request_control_key_returns_400(self):
        account = ObjectGenerator.create_account()
        payload = PayloadGenerator.create_deposit_payload()
        del payload["request_control_key"]

        status, response = RequestGenerator.POST_transaction(account["account_key"], payload)

        assert status == 400
        assert response["code"] == "QIT000001"

    def test_deposit_with_destination_returns_400(self):
        """O destino só faz sentido em transferência; o schema recusa a mistura."""
        account = ObjectGenerator.create_account()
        payload = PayloadGenerator.create_deposit_payload(destination_account_key=RandomGenerator.generate_uuid())

        status, response = RequestGenerator.POST_transaction(account["account_key"], payload)

        assert status == 400
        assert response["code"] == "QIT000001"
