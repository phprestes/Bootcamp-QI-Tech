from requests.exceptions import RequestException

from connectors.rest_connector import BaseConnectorResponse, RestConnector
from constants import BUREAU_API_INTERNAL_TOKEN, BUREAU_API_TIMEOUT, BUREAU_API_URL
from errors import BureauUnavailable


class BureauConnector(RestConnector):
    """Fala com o birô de CPF. Traduz "não respondeu" em erro nosso; o que cada status significa é o controller que decide."""

    def __init__(self) -> None:
        super().__init__(
            class_name=__name__,
            base_url=BUREAU_API_URL,
            timeout=BUREAU_API_TIMEOUT,
            internal_token=BUREAU_API_INTERNAL_TOKEN,
        )

    def get_document_situation(self, document_number: str) -> BaseConnectorResponse:
        digits = "".join(character for character in document_number if character.isdigit())

        try:
            return self.send(endpoint=f"/documents/{digits}", method="GET")
        except RequestException as exception:
            self.logger.error(f"Birô sem resposta: {exception.__class__.__name__}")
            raise BureauUnavailable("no response")
