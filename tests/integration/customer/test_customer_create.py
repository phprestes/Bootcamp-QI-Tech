from tests.utils import (
    BureauMock,
    ObjectGenerator,
    PayloadGenerator,
    RequestGenerator,
    birthdate_for_age,
)


ERROR_FIELDS = {"title", "description", "translation", "code"}
INVALID_CHECK_DIGIT_CPF = "529.982.247-24"


class TestCustomerCreate:
    def test_post_customer_returns_201_with_key(self):
        """RN02/RN03 (caminho que passa): CPF válido, novo e regular vira cliente."""
        payload = PayloadGenerator.create_customer_payload()
        BureauMock.regular(payload["document_number"])

        status, response = RequestGenerator.POST_customer(payload)

        assert status == 201
        assert len(response["customer_key"]) == 36

    def test_post_customer_calls_bureau_once_with_its_token(self):
        """RN05: o birô é consultado uma vez e recebe o INTERNAL-TOKEN dele."""
        payload = PayloadGenerator.create_customer_payload()
        BureauMock.regular(payload["document_number"])

        status, _ = RequestGenerator.POST_customer(payload)

        calls = BureauMock.received_calls(payload["document_number"])
        assert status == 201
        assert len(calls) == 1
        assert "INTERNAL-TOKEN" in calls[0]["headers"]

    def test_post_customer_with_empty_body_returns_400(self):
        status, response = RequestGenerator.POST_customer({})

        assert status == 400
        assert response["code"] == "QIT000001"

    def test_post_customer_with_unknown_field_returns_400(self):
        """Mass assignment: campo fora do contrato é recusado, não ignorado."""
        payload = PayloadGenerator.create_customer_payload(balance=1000000)

        status, response = RequestGenerator.POST_customer(payload)

        assert status == 400
        assert response["code"] == "QIT000001"

    def test_post_customer_with_unmasked_cpf_returns_400(self):
        """RN01: formato é assunto do schema."""
        payload = PayloadGenerator.create_customer_payload(document_number="52998224725")

        status, response = RequestGenerator.POST_customer(payload)

        assert status == 400
        assert response["code"] == "QIT000001"

    def test_post_customer_with_invalid_cpf_returns_422(self):
        """RN02: dígito verificador errado; o birô nem é chamado."""
        payload = PayloadGenerator.create_customer_payload(document_number=INVALID_CHECK_DIGIT_CPF)

        status, response = RequestGenerator.POST_customer(payload)

        assert status == 422
        assert response["code"] == "QIT002003"
        assert set(response) == ERROR_FIELDS
        assert BureauMock.received_calls(INVALID_CHECK_DIGIT_CPF) == []

    def test_post_customer_with_duplicate_cpf_returns_409(self):
        """RN03: o segundo cadastro do mesmo CPF é barrado antes do birô."""
        customer = ObjectGenerator.create_customer()
        calls_before = len(BureauMock.received_calls(customer["document_number"]))

        payload = PayloadGenerator.create_customer_payload(document_number=customer["document_number"])
        status, response = RequestGenerator.POST_customer(payload)

        assert status == 409
        assert response["code"] == "QIT002002"
        assert len(BureauMock.received_calls(customer["document_number"])) == calls_before

    def test_post_customer_adult_returns_201(self):
        """RN04 (caminho que passa): quem faz 18 hoje já pode."""
        payload = PayloadGenerator.create_customer_payload(birthdate=birthdate_for_age(18))
        BureauMock.regular(payload["document_number"])

        status, _ = RequestGenerator.POST_customer(payload)

        assert status == 201

    def test_post_customer_underage_returns_422(self):
        """RN04: menor de 18 é recusado sem consultar o birô."""
        payload = PayloadGenerator.create_customer_payload(birthdate=birthdate_for_age(17))
        BureauMock.regular(payload["document_number"])

        status, response = RequestGenerator.POST_customer(payload)

        assert status == 422
        assert response["code"] == "QIT002004"
        assert BureauMock.received_calls(payload["document_number"]) == []

    def test_post_customer_with_impossible_date_returns_422(self):
        payload = PayloadGenerator.create_customer_payload(birthdate="1990-02-30")

        status, response = RequestGenerator.POST_customer(payload)

        assert status == 422
        assert response["code"] == "QIT002017"

    def test_post_customer_suspended_cpf_returns_422(self):
        """RN05: CPF irregular no birô não vira cliente."""
        payload = PayloadGenerator.create_customer_payload()
        BureauMock.suspended(payload["document_number"])

        status, response = RequestGenerator.POST_customer(payload)

        assert status == 422
        assert response["code"] == "QIT002005"

    def test_post_customer_unknown_to_bureau_returns_422(self):
        payload = PayloadGenerator.create_customer_payload()
        BureauMock.not_found(payload["document_number"])

        status, response = RequestGenerator.POST_customer(payload)

        assert status == 422
        assert response["code"] == "QIT002005"

    def test_post_customer_bureau_down_returns_502(self):
        """RN06: birô com 500 vira 502, e nada é gravado."""
        payload = PayloadGenerator.create_customer_payload()
        BureauMock.server_error(payload["document_number"])

        status, response = RequestGenerator.POST_customer(payload)

        assert status == 502
        assert response["code"] == "QIT002006"
        status, page = RequestGenerator.GET_customers({"document_number": payload["document_number"]})
        assert status == 200
        assert page["data"] == []

    def test_post_customer_bureau_connection_dropped_returns_502(self):
        payload = PayloadGenerator.create_customer_payload()
        BureauMock.connection_dropped(payload["document_number"])

        status, response = RequestGenerator.POST_customer(payload)

        assert status == 502
        assert response["code"] == "QIT002006"

    def test_post_customer_bureau_unexpected_body_returns_502(self):
        """API10: resposta do birô sem `situation` não é confiada."""
        payload = PayloadGenerator.create_customer_payload()
        BureauMock.unexpected_body(payload["document_number"])

        status, response = RequestGenerator.POST_customer(payload)

        assert status == 502
        assert response["code"] == "QIT002006"

    def test_post_customer_bureau_timeout_returns_502(self):
        """RN06: birô mais lento que o timeout do connector (padrão 5s) vira 502."""
        payload = PayloadGenerator.create_customer_payload()
        BureauMock.slower_than_timeout(payload["document_number"], delay_seconds=7)

        status, response = RequestGenerator.POST_customer(payload)

        assert status == 502
        assert response["code"] == "QIT002006"

    def test_post_customer_after_bureau_failure_can_be_retried(self):
        """Falha do birô não grava nada: repetir depois funciona."""
        payload = PayloadGenerator.create_customer_payload()
        BureauMock.server_error(payload["document_number"], times=1)
        BureauMock.regular(payload["document_number"])

        first_status, _ = RequestGenerator.POST_customer(payload)
        retry_status, _ = RequestGenerator.POST_customer(payload)

        assert first_status == 502
        assert retry_status == 201
