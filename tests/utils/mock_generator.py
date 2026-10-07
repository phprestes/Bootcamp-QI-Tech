from tests.utils.mock_utils import BaseExpectation, Mock


BUREAU_PREFIX = "/bureau/documents"


def bureau_path(document_number: str) -> str:
    """Caminho que a API chama para um CPF; o connector manda só os dígitos."""
    digits = "".join(character for character in document_number if character.isdigit())
    return f"{BUREAU_PREFIX}/{digits}"


class BureauMock:
    """Roteiro das respostas do birô. Cada expectation vale para um CPF só, então os testes não interferem entre si."""

    @staticmethod
    def situation(document_number: str, situation: str) -> None:
        Mock().add_expectations(
            BaseExpectation.generate_expectation(
                "GET",
                bureau_path(document_number),
                status_code=200,
                response_json={"document_number": document_number, "situation": situation},
            )
        )

    @staticmethod
    def regular(document_number: str) -> None:
        BureauMock.situation(document_number, "REGULAR")

    @staticmethod
    def suspended(document_number: str) -> None:
        BureauMock.situation(document_number, "SUSPENDED")

    @staticmethod
    def not_found(document_number: str) -> None:
        Mock().add_expectations(
            BaseExpectation.generate_expectation(
                "GET",
                bureau_path(document_number),
                status_code=404,
                response_json={"code": "DOCUMENT_NOT_FOUND"},
            )
        )

    @staticmethod
    def server_error(document_number: str, times: int = None) -> None:
        """Com `times`, a falha vale só nas primeiras chamadas; depois vale a próxima expectation."""
        Mock().add_expectations(
            BaseExpectation.generate_expectation(
                "GET",
                bureau_path(document_number),
                status_code=500,
                response_json={"code": "INTERNAL_ERROR"},
                number_of_calls=times,
            )
        )

    @staticmethod
    def unexpected_body(document_number: str) -> None:
        Mock().add_expectations(
            BaseExpectation.generate_expectation(
                "GET",
                bureau_path(document_number),
                status_code=200,
                response_json={"unexpected": True},
            )
        )

    @staticmethod
    def connection_dropped(document_number: str) -> None:
        Mock().add_expectations(
            BaseExpectation.generate_error("GET", bureau_path(document_number), error_json={"dropConnection": True})
        )

    @staticmethod
    def slower_than_timeout(document_number: str, delay_seconds: int) -> None:
        expectation = BaseExpectation.generate_expectation(
            "GET",
            bureau_path(document_number),
            status_code=200,
            response_json={"document_number": document_number, "situation": "REGULAR"},
        )
        expectation["httpResponse"]["delay"] = {"timeUnit": "SECONDS", "value": delay_seconds}
        Mock().add_expectations(expectation)

    @staticmethod
    def received_calls(document_number: str) -> list:
        return Mock().retrieve_requests("GET", bureau_path(document_number))
