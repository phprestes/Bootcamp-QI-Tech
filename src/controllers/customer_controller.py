from datetime import date

from sqlalchemy.exc import IntegrityError

from connectors import BureauConnector
from constants import MINIMUM_CUSTOMER_AGE
from controllers.base_controller import BaseController
from dtos import CustomerDTO
from errors import (
    BureauUnavailable,
    DuplicatedDocumentNumber,
    InvalidBirthdate,
    InvalidDocumentNumber,
    IrregularDocumentNumber,
    NotFoundCustomer,
    UnderageCustomer,
)
from models import Customer
from repositories import CustomerRepository
from utils.document_number import is_valid_cpf


REGULAR_SITUATION = "REGULAR"


class CustomerController(BaseController):
    """Cadastro de cliente. Fluxo e ramos de falha: docs/05-fluxos/criar-cliente.md."""

    def __init__(self) -> None:
        super().__init__(__name__)
        self.customer_repository = CustomerRepository(self.context)
        self.bureau_connector = BureauConnector()

    def create(self, customer_data: dict) -> dict:
        """Tudo que se responde localmente vem antes do birô: não se gasta chamada externa com pedido que será recusado."""
        document_number = customer_data["document_number"]

        if not is_valid_cpf(document_number):
            raise InvalidDocumentNumber()

        birthdate = self._parse_birthdate(customer_data["birthdate"])
        self._check_age(birthdate)

        if self.customer_repository.get_by_document_number(document_number) is not None:
            raise DuplicatedDocumentNumber()

        self._check_bureau(document_number)

        try:
            customer = self.customer_repository.create({**customer_data, "birthdate": birthdate})
            customer_dto = CustomerDTO.only_obj_key(customer)
            self.session.commit()
        except IntegrityError:
            # Dois cadastros simultâneos do mesmo CPF passam da checagem acima; o UNIQUE decide.
            self.session.rollback()
            raise DuplicatedDocumentNumber()

        self.logger.info("Cliente cadastrado")

        return customer_dto

    def get_by_key(self, customer_key: str) -> dict:
        return CustomerDTO.obj_to_dict(self.get_customer(customer_key))

    def get_list(self, limit: int, offset: int, document_number: str = None) -> dict:
        customers = self.customer_repository.list_page(limit, offset, document_number)

        is_last_page = len(customers) <= limit

        return {
            "data": CustomerDTO.list_obj_to_list_dict(customers[:limit]),
            "is_last_page": is_last_page,
        }

    def get_customer(self, customer_key: str) -> Customer:
        customer = self.customer_repository.get_by_key(customer_key)

        if customer is None:
            raise NotFoundCustomer(customer_key)

        return customer

    def _parse_birthdate(self, raw_birthdate: str) -> date:
        try:
            birthdate = date.fromisoformat(raw_birthdate)
        except ValueError:
            raise InvalidBirthdate(raw_birthdate)

        if birthdate > date.today():
            raise InvalidBirthdate(raw_birthdate)

        return birthdate

    def _check_age(self, birthdate: date) -> None:
        today = date.today()
        had_birthday_this_year = (today.month, today.day) >= (birthdate.month, birthdate.day)
        age = today.year - birthdate.year - (0 if had_birthday_this_year else 1)

        if age < MINIMUM_CUSTOMER_AGE:
            raise UnderageCustomer(MINIMUM_CUSTOMER_AGE)

    def _check_bureau(self, document_number: str) -> None:
        """O connector entrega a resposta crua; aqui se decide o que cada uma significa (docs/06-operacao/resiliencia.md)."""
        response = self.bureau_connector.get_document_situation(document_number)

        if response.status == 404:
            raise IrregularDocumentNumber("UNKNOWN")

        if response.status != 200:
            self.logger.error(f"Birô respondeu {response.status}")
            raise BureauUnavailable(f"unexpected status {response.status}")

        situation = (response.json or {}).get("situation")

        if not isinstance(situation, str):
            raise BureauUnavailable("response without situation")

        if situation != REGULAR_SITUATION:
            self.logger.info(f"Cadastro recusado: CPF {situation} no birô")
            raise IrregularDocumentNumber(situation)
