from tests.utils import ObjectGenerator, PayloadGenerator, RandomGenerator, RequestGenerator


CREDIT_TYPES = {"DEPOSIT", "TRANSFER_IN"}
DEBIT_TYPES = {"TRANSFER_OUT", "FEE"}


def read_whole_statement(account_key: str, limit: int = 2) -> list:
    items = []
    page = 0
    while True:
        status, response = RequestGenerator.GET_transactions(account_key, {"limit": str(limit), "page": str(page)})
        assert status == 200
        items.extend(response["data"])
        if response["is_last_page"]:
            return items
        page += 1


class TestStatement:
    def test_statement_pagination_envelope(self):
        """RN21: envelope data/limit/page/is_last_page, do mais novo para o mais antigo."""
        account = ObjectGenerator.create_account()
        for amount in (100, 200, 300):
            ObjectGenerator.deposit(account["account_key"], amount)

        status, first_page = RequestGenerator.GET_transactions(account["account_key"], {"limit": "2", "page": "0"})
        _, last_page = RequestGenerator.GET_transactions(account["account_key"], {"limit": "2", "page": "1"})

        assert status == 200
        assert set(first_page) == {"data", "limit", "page", "is_last_page"}
        assert [item["amount"] for item in first_page["data"]] == [300, 200]
        assert first_page["is_last_page"] is False
        assert [item["amount"] for item in last_page["data"]] == [100]
        assert last_page["is_last_page"] is True

    def test_statement_page_beyond_end_is_empty(self):
        account = ObjectGenerator.create_account_with_balance(100)

        status, response = RequestGenerator.GET_transactions(account["account_key"], {"page": "5"})

        assert status == 200
        assert response["data"] == []
        assert response["is_last_page"] is True

    def test_statement_filters_by_type(self):
        origin = ObjectGenerator.create_account_with_balance(10000)
        destination = ObjectGenerator.create_account()
        RequestGenerator.POST_transaction(
            origin["account_key"], PayloadGenerator.create_transfer_payload(destination["account_key"], amount=100)
        )

        status, response = RequestGenerator.GET_transactions(origin["account_key"], {"type": "FEE"})

        assert status == 200
        assert [(item["type"], item["direction"]) for item in response["data"]] == [("FEE", "DEBIT")]

    def test_statement_rebuilds_balance(self):
        """R4: a soma do extrato reconstrói o saldo; nada some."""
        origin = ObjectGenerator.create_account_with_balance(50000)
        destination = ObjectGenerator.create_account_with_balance(700)
        for amount in (1000, 2500):
            RequestGenerator.POST_transaction(
                origin["account_key"], PayloadGenerator.create_transfer_payload(destination["account_key"], amount)
            )
        RequestGenerator.POST_transaction(
            destination["account_key"], PayloadGenerator.create_transfer_payload(origin["account_key"], 300)
        )

        for account in (origin, destination):
            items = read_whole_statement(account["account_key"])
            credits = sum(item["amount"] for item in items if item["type"] in CREDIT_TYPES)
            debits = sum(item["amount"] for item in items if item["type"] in DEBIT_TYPES)
            assert credits - debits == ObjectGenerator.get_balance(account["account_key"])

    def test_statement_limit_over_100_returns_400(self):
        account = ObjectGenerator.create_account()

        status, response = RequestGenerator.GET_transactions(account["account_key"], {"limit": "101"})

        assert status == 400
        assert response["code"] == "QIT000001"

    def test_statement_limit_zero_returns_400(self):
        account = ObjectGenerator.create_account()

        status, response = RequestGenerator.GET_transactions(account["account_key"], {"limit": "0"})

        assert status == 400
        assert response["code"] == "QIT000001"

    def test_statement_of_unknown_account_returns_404(self):
        status, response = RequestGenerator.GET_transactions(RandomGenerator.generate_uuid())

        assert status == 404
        assert response["code"] == "QIT002007"

    def test_get_transaction_of_own_account_returns_200(self):
        account = ObjectGenerator.create_account()
        deposit = ObjectGenerator.deposit(account["account_key"], 1234)

        status, response = RequestGenerator.GET_transaction(account["account_key"], deposit["transaction_key"])

        assert status == 200
        assert response["transaction_key"] == deposit["transaction_key"]
        assert response["amount"] == 1234
        assert response["direction"] == "CREDIT"

    def test_get_transaction_of_other_account_returns_404(self):
        """R8/RN20: o lançamento existe, mas não é desta conta: 404, nunca 403."""
        owner = ObjectGenerator.create_account()
        intruder = ObjectGenerator.create_account()
        deposit = ObjectGenerator.deposit(owner["account_key"], 1234)

        status, response = RequestGenerator.GET_transaction(intruder["account_key"], deposit["transaction_key"])

        assert status == 404
        assert response["code"] == "QIT002015"
