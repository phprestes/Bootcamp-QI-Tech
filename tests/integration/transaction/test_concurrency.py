from concurrent.futures import ThreadPoolExecutor

from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator


TRANSFER_FEE_CENTS = 200
PARALLEL_REQUESTS = 10


def transfer(origin_key: str, destination_key: str, amount: int) -> int:
    status, _ = RequestGenerator.POST_transaction(
        origin_key, PayloadGenerator.create_transfer_payload(destination_key, amount=amount)
    )
    return status


class TestConcurrency:
    def test_concurrent_transfers_never_make_balance_negative(self):
        """Principal desafio: 10 transferências simultâneas, saldo para 3; só 3 passam."""
        amount = 1000
        origin = ObjectGenerator.create_account_with_balance(3 * (amount + TRANSFER_FEE_CENTS))
        destination = ObjectGenerator.create_account()

        with ThreadPoolExecutor(max_workers=PARALLEL_REQUESTS) as pool:
            statuses = list(
                pool.map(
                    lambda _: transfer(origin["account_key"], destination["account_key"], amount),
                    range(PARALLEL_REQUESTS),
                )
            )

        assert sorted(statuses) == [201] * 3 + [422] * (PARALLEL_REQUESTS - 3)
        assert ObjectGenerator.get_balance(origin["account_key"]) == 0
        assert ObjectGenerator.get_balance(destination["account_key"]) == 3 * amount

    def test_crossed_transfers_do_not_deadlock(self):
        """A→B e B→A ao mesmo tempo: lock em ordem de id evita deadlock; todas terminam."""
        first = ObjectGenerator.create_account_with_balance(100000)
        second = ObjectGenerator.create_account_with_balance(100000)
        pairs = [(first, second), (second, first)] * (PARALLEL_REQUESTS // 2)

        with ThreadPoolExecutor(max_workers=PARALLEL_REQUESTS) as pool:
            statuses = list(pool.map(lambda pair: transfer(pair[0]["account_key"], pair[1]["account_key"], 100), pairs))

        assert statuses == [201] * PARALLEL_REQUESTS
        total = ObjectGenerator.get_balance(first["account_key"]) + ObjectGenerator.get_balance(second["account_key"])
        assert total == 200000 - PARALLEL_REQUESTS * TRANSFER_FEE_CENTS
