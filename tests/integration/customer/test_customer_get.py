from tests.utils import ObjectGenerator, RandomGenerator, RequestGenerator


def assert_no_internal_ids(value) -> None:
    """R5: nenhuma resposta carrega o id do banco nem FK numérica."""
    if isinstance(value, dict):
        for field, nested in value.items():
            assert field != "id" and not field.endswith("_id"), field
            assert_no_internal_ids(nested)
    elif isinstance(value, list):
        for item in value:
            assert_no_internal_ids(item)


class TestCustomerGet:
    def test_get_customer_returns_200(self):
        customer = ObjectGenerator.create_customer()

        status, response = RequestGenerator.GET_customer(customer["customer_key"])

        assert status == 200
        assert response["customer_key"] == customer["customer_key"]
        assert response["document_number"] == customer["document_number"]
        assert response["birthdate"] == customer["birthdate"]
        assert_no_internal_ids(response)

    def test_get_unknown_customer_returns_404(self):
        status, response = RequestGenerator.GET_customer(RandomGenerator.generate_uuid())

        assert status == 404
        assert response["code"] == "QIT002001"

    def test_get_customers_filters_by_document_number(self):
        customer = ObjectGenerator.create_customer()

        status, response = RequestGenerator.GET_customers({"document_number": customer["document_number"]})

        assert status == 200
        assert [item["customer_key"] for item in response["data"]] == [customer["customer_key"]]
        assert response["is_last_page"] is True
        assert_no_internal_ids(response)

    def test_get_customers_pagination_envelope(self):
        ObjectGenerator.create_customer()
        ObjectGenerator.create_customer()

        status, response = RequestGenerator.GET_customers({"limit": "1", "page": "0"})

        assert status == 200
        assert set(response) == {"data", "limit", "page", "is_last_page"}
        assert len(response["data"]) == 1
        assert response["limit"] == 1
        assert response["page"] == 0
        assert response["is_last_page"] is False

    def test_get_customers_with_limit_over_100_returns_400(self):
        status, response = RequestGenerator.GET_customers({"limit": "101"})

        assert status == 400
        assert response["code"] == "QIT000001"

    def test_get_customers_with_unknown_param_returns_400(self):
        status, response = RequestGenerator.GET_customers({"order": "name"})

        assert status == 400
        assert response["code"] == "QIT000001"

    def test_get_customer_accounts_lists_only_own_accounts(self):
        """R8: a lista aninhada só traz contas do cliente do caminho."""
        owner = ObjectGenerator.create_account()
        ObjectGenerator.create_account()

        status, response = RequestGenerator.GET_customer_accounts(owner["customer_key"])

        assert status == 200
        assert [item["account_key"] for item in response["data"]] == [owner["account_key"]]

    def test_get_accounts_of_unknown_customer_returns_404(self):
        status, response = RequestGenerator.GET_customer_accounts(RandomGenerator.generate_uuid())

        assert status == 404
        assert response["code"] == "QIT002001"
