from tests.utils import ObjectGenerator, PayloadGenerator, RandomGenerator, RequestGenerator


def change_status(account_key: str, status: str) -> tuple:
    return RequestGenerator.PUT_account_status(account_key, PayloadGenerator.create_status_payload(status))


class TestAccountStatus:
    def test_put_account_status_block_and_unblock(self):
        """RN10: ACTIVE ⇄ BLOCKED, e cada transição vira evento."""
        account = ObjectGenerator.create_account()

        blocked_status, blocked = change_status(account["account_key"], "BLOCKED")
        active_status, active = change_status(account["account_key"], "ACTIVE")
        _, current = RequestGenerator.GET_account(account["account_key"])

        assert (blocked_status, blocked["status"]) == (200, "BLOCKED")
        assert (active_status, active["status"]) == (200, "ACTIVE")
        assert [event["to_status"] for event in current["status_events"]] == ["ACTIVE", "BLOCKED", "ACTIVE"]
        assert current["status_events"][2]["reason"] == "requested by test"

    def test_put_account_status_close_with_zero_balance_returns_200(self):
        account = ObjectGenerator.create_account()

        status, response = change_status(account["account_key"], "CLOSED")

        assert status == 200
        assert response["status"] == "CLOSED"

    def test_put_account_status_closed_is_final_returns_409(self):
        """RN10: CLOSED é estado final."""
        account = ObjectGenerator.create_account()
        change_status(account["account_key"], "CLOSED")

        status, response = change_status(account["account_key"], "ACTIVE")

        assert status == 409
        assert response["code"] == "QIT002010"

    def test_put_account_status_same_status_returns_409(self):
        account = ObjectGenerator.create_account()

        status, response = change_status(account["account_key"], "ACTIVE")

        assert status == 409
        assert response["code"] == "QIT002010"

    def test_close_blocked_account_returns_409(self):
        """RN10: precisa desbloquear antes de encerrar."""
        account = ObjectGenerator.create_account()
        change_status(account["account_key"], "BLOCKED")

        status, response = change_status(account["account_key"], "CLOSED")

        assert status == 409
        assert response["code"] == "QIT002010"

    def test_close_account_with_balance_returns_409(self):
        """RN11: só encerra com saldo 0."""
        account = ObjectGenerator.create_account_with_balance(100)

        status, response = change_status(account["account_key"], "CLOSED")

        assert status == 409
        assert response["code"] == "QIT002011"

    def test_put_account_status_unknown_status_returns_400(self):
        account = ObjectGenerator.create_account()

        status, response = change_status(account["account_key"], "FROZEN")

        assert status == 400
        assert response["code"] == "QIT000001"

    def test_put_status_of_unknown_account_returns_404(self):
        status, response = change_status(RandomGenerator.generate_uuid(), "BLOCKED")

        assert status == 404
        assert response["code"] == "QIT002007"
