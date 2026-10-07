from tests.utils import ObjectGenerator, RandomGenerator, RequestGenerator


MAX_ACCOUNTS_PER_CUSTOMER = 3


class TestAccountCreate:
    def test_post_account_returns_201_active_zero_balance(self):
        """RN09: a conta nasce ACTIVE, com saldo 0."""
        customer = ObjectGenerator.create_customer()

        status, response = RequestGenerator.POST_account(customer["customer_key"])

        assert status == 201
        assert len(response["account_key"]) == 36
        assert response["status"] == "ACTIVE"
        assert response["balance"] == 0

    def test_new_account_history_starts_at_opening(self):
        """RN09: o primeiro evento registra o nascimento (de nada para ACTIVE)."""
        account = ObjectGenerator.create_account()

        status, response = RequestGenerator.GET_account(account["account_key"])

        assert status == 200
        assert response["customer_key"] == account["customer_key"]
        assert [(event["from_status"], event["to_status"]) for event in response["status_events"]] == [
            (None, "ACTIVE")
        ]

    def test_post_account_unknown_customer_returns_404(self):
        """RN07: key que não existe é 404, não 422."""
        status, response = RequestGenerator.POST_account(RandomGenerator.generate_uuid())

        assert status == 404
        assert response["code"] == "QIT002001"

    def test_post_account_up_to_limit_returns_201(self):
        customer = ObjectGenerator.create_customer()

        statuses = [RequestGenerator.POST_account(customer["customer_key"])[0] for _ in range(MAX_ACCOUNTS_PER_CUSTOMER)]

        assert statuses == [201] * MAX_ACCOUNTS_PER_CUSTOMER

    def test_post_account_over_limit_returns_409(self):
        """RN08: a quarta conta não encerrada é recusada."""
        customer = ObjectGenerator.create_customer()
        for _ in range(MAX_ACCOUNTS_PER_CUSTOMER):
            ObjectGenerator.create_account(customer["customer_key"])

        status, response = RequestGenerator.POST_account(customer["customer_key"])

        assert status == 409
        assert response["code"] == "QIT002008"

    def test_closed_account_frees_a_slot(self):
        """RN08: conta encerrada não conta no limite."""
        customer = ObjectGenerator.create_customer()
        accounts = [ObjectGenerator.create_account(customer["customer_key"]) for _ in range(MAX_ACCOUNTS_PER_CUSTOMER)]
        RequestGenerator.PUT_account_status(accounts[0]["account_key"], {"status": "CLOSED"})

        status, _ = RequestGenerator.POST_account(customer["customer_key"])

        assert status == 201

    def test_get_unknown_account_returns_404(self):
        status, response = RequestGenerator.GET_account(RandomGenerator.generate_uuid())

        assert status == 404
        assert response["code"] == "QIT002007"
