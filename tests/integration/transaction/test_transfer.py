from tests.utils import ObjectGenerator, PayloadGenerator, RandomGenerator, RequestGenerator


TRANSFER_FEE_CENTS = 200


class TestTransfer:
    def test_transfer_debits_amount_plus_fee_and_credits_destination(self):
        """RN14 + RN17: origem perde valor + tarifa; destino ganha só o valor."""
        origin = ObjectGenerator.create_account_with_balance(100000)
        destination = ObjectGenerator.create_account()

        status, response = RequestGenerator.POST_transaction(
            origin["account_key"], PayloadGenerator.create_transfer_payload(destination["account_key"], amount=20000)
        )

        assert status == 201
        assert response["type"] == "TRANSFER_OUT"
        assert response["amount"] == 20000
        assert response["fee"] == TRANSFER_FEE_CENTS
        assert response["balance"] == 100000 - 20000 - TRANSFER_FEE_CENTS
        assert ObjectGenerator.get_balance(origin["account_key"]) == 79800
        assert ObjectGenerator.get_balance(destination["account_key"]) == 20000

    def test_transfer_of_exact_balance_minus_fee_leaves_zero(self):
        """RN14 (caminho que passa no limite): saldo igual a valor + tarifa é suficiente."""
        origin = ObjectGenerator.create_account_with_balance(10200)
        destination = ObjectGenerator.create_account()

        status, _ = RequestGenerator.POST_transaction(
            origin["account_key"], PayloadGenerator.create_transfer_payload(destination["account_key"], amount=10000)
        )

        assert status == 201
        assert ObjectGenerator.get_balance(origin["account_key"]) == 0

    def test_transfer_without_balance_returns_422_and_keeps_both_balances(self):
        """RN14: saldo menor que valor + tarifa não move dinheiro em nenhuma conta."""
        origin = ObjectGenerator.create_account_with_balance(10000)
        destination = ObjectGenerator.create_account()

        status, response = RequestGenerator.POST_transaction(
            origin["account_key"], PayloadGenerator.create_transfer_payload(destination["account_key"], amount=10000)
        )

        assert status == 422
        assert response["code"] == "QIT002012"
        assert ObjectGenerator.get_balance(origin["account_key"]) == 10000
        assert ObjectGenerator.get_balance(destination["account_key"]) == 0

    def test_transfer_to_same_account_returns_422(self):
        """RN15."""
        origin = ObjectGenerator.create_account_with_balance(10000)

        status, response = RequestGenerator.POST_transaction(
            origin["account_key"], PayloadGenerator.create_transfer_payload(origin["account_key"], amount=100)
        )

        assert status == 422
        assert response["code"] == "QIT002013"

    def test_transfer_to_unknown_account_returns_404(self):
        """RN16."""
        origin = ObjectGenerator.create_account_with_balance(10000)

        status, response = RequestGenerator.POST_transaction(
            origin["account_key"], PayloadGenerator.create_transfer_payload(RandomGenerator.generate_uuid())
        )

        assert status == 404
        assert response["code"] == "QIT002014"
        assert ObjectGenerator.get_balance(origin["account_key"]) == 10000

    def test_transfer_from_blocked_account_returns_409(self):
        """RN12: origem fora de ACTIVE."""
        origin = ObjectGenerator.create_account_with_balance(10000)
        destination = ObjectGenerator.create_account()
        RequestGenerator.PUT_account_status(origin["account_key"], {"status": "BLOCKED"})

        status, response = RequestGenerator.POST_transaction(
            origin["account_key"], PayloadGenerator.create_transfer_payload(destination["account_key"], amount=100)
        )

        assert status == 409
        assert response["code"] == "QIT002009"

    def test_transfer_to_closed_account_returns_409(self):
        """RN12: destino fora de ACTIVE; nenhum saldo muda."""
        origin = ObjectGenerator.create_account_with_balance(10000)
        destination = ObjectGenerator.create_account()
        RequestGenerator.PUT_account_status(destination["account_key"], {"status": "CLOSED"})

        status, response = RequestGenerator.POST_transaction(
            origin["account_key"], PayloadGenerator.create_transfer_payload(destination["account_key"], amount=100)
        )

        assert status == 409
        assert response["code"] == "QIT002009"
        assert ObjectGenerator.get_balance(origin["account_key"]) == 10000

    def test_transfer_without_destination_returns_400(self):
        origin = ObjectGenerator.create_account_with_balance(10000)
        payload = PayloadGenerator.create_transfer_payload("x")
        del payload["destination_account_key"]

        status, response = RequestGenerator.POST_transaction(origin["account_key"], payload)

        assert status == 400
        assert response["code"] == "QIT000001"

    def test_transfer_is_visible_in_both_statements(self):
        """RN17: a tarifa aparece como lançamento próprio no extrato da origem."""
        origin = ObjectGenerator.create_account_with_balance(50000)
        destination = ObjectGenerator.create_account()
        RequestGenerator.POST_transaction(
            origin["account_key"], PayloadGenerator.create_transfer_payload(destination["account_key"], amount=1000)
        )

        _, origin_statement = RequestGenerator.GET_transactions(origin["account_key"])
        _, destination_statement = RequestGenerator.GET_transactions(destination["account_key"])

        assert sorted(item["type"] for item in origin_statement["data"]) == ["DEPOSIT", "FEE", "TRANSFER_OUT"]
        assert [item["type"] for item in destination_statement["data"]] == ["TRANSFER_IN"]
        assert destination_statement["data"][0]["counterpart_account_key"] == origin["account_key"]
