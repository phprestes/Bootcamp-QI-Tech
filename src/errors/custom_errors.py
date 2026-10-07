"""Recusas do domínio do banco. Catálogo e regra de cada código: docs/03-api/erros.md."""

from errors import QIException


class NotFoundCustomer(QIException):
    code = "QIT002001"

    def __init__(self, customer_key) -> None:
        title = "Customer not Found"
        http_status = 404
        description = f"Customer with key {customer_key} was not found."
        translation = f"O cliente com chave {customer_key} não foi encontrado."
        super().__init__(title, self.code, http_status, description, translation)


class DuplicatedDocumentNumber(QIException):
    code = "QIT002002"

    def __init__(self) -> None:
        title = "Document number already registered"
        http_status = 409
        description = "There is already a customer with this document number."
        translation = "Já existe um cliente cadastrado com este CPF."
        super().__init__(title, self.code, http_status, description, translation)


class InvalidDocumentNumber(QIException):
    code = "QIT002003"

    def __init__(self) -> None:
        title = "Invalid document number"
        http_status = 422
        description = "The document number check digits do not match."
        translation = "Os dígitos verificadores do CPF não conferem."
        super().__init__(title, self.code, http_status, description, translation)


class UnderageCustomer(QIException):
    code = "QIT002004"

    def __init__(self, minimum_age: int) -> None:
        title = "Underage customer"
        http_status = 422
        description = f"Customer must be at least {minimum_age} years old."
        translation = f"O cliente precisa ter pelo menos {minimum_age} anos."
        super().__init__(title, self.code, http_status, description, translation)


class IrregularDocumentNumber(QIException):
    code = "QIT002005"

    def __init__(self, situation: str) -> None:
        title = "Irregular document number"
        http_status = 422
        description = f"The bureau reports the document number as {situation}."
        translation = "O CPF não está regular no birô."
        super().__init__(title, self.code, http_status, description, translation)


class BureauUnavailable(QIException):
    code = "QIT002006"

    def __init__(self, reason: str) -> None:
        title = "Bureau unavailable"
        http_status = 502
        description = f"The document bureau could not be used: {reason}."
        translation = "O birô de CPF está indisponível. Tente novamente."
        super().__init__(title, self.code, http_status, description, translation)


class NotFoundAccount(QIException):
    code = "QIT002007"

    def __init__(self, account_key) -> None:
        title = "Account not Found"
        http_status = 404
        description = f"Account with key {account_key} was not found."
        translation = f"A conta com chave {account_key} não foi encontrada."
        super().__init__(title, self.code, http_status, description, translation)


class AccountLimitReached(QIException):
    code = "QIT002008"

    def __init__(self, limit: int) -> None:
        title = "Account limit reached"
        http_status = 409
        description = f"Customer already has {limit} accounts that are not closed."
        translation = f"O cliente já tem {limit} contas não encerradas."
        super().__init__(title, self.code, http_status, description, translation)


class AccountNotActive(QIException):
    code = "QIT002009"

    def __init__(self, account_key, status: str) -> None:
        title = "Account not active"
        http_status = 409
        description = f"Account {account_key} is {status} and cannot move money."
        translation = f"A conta {account_key} está {status} e não pode movimentar dinheiro."
        super().__init__(title, self.code, http_status, description, translation)


class InvalidStatusTransition(QIException):
    code = "QIT002010"

    def __init__(self, from_status: str, to_status: str) -> None:
        title = "Invalid status transition"
        http_status = 409
        description = f"Account cannot go from {from_status} to {to_status}."
        translation = f"A conta não pode passar de {from_status} para {to_status}."
        super().__init__(title, self.code, http_status, description, translation)


class AccountHasBalance(QIException):
    code = "QIT002011"

    def __init__(self) -> None:
        title = "Account has balance"
        http_status = 409
        description = "Only accounts with zero balance can be closed."
        translation = "Só é possível encerrar conta com saldo zero."
        super().__init__(title, self.code, http_status, description, translation)


class InsufficientBalance(QIException):
    code = "QIT002012"

    def __init__(self) -> None:
        title = "Insufficient Balance"
        http_status = 422
        description = "Origin account balance does not cover amount plus fee."
        translation = "Saldo insuficiente para o valor mais a tarifa."
        super().__init__(title, self.code, http_status, description, translation)


class SameAccountTransfer(QIException):
    code = "QIT002013"

    def __init__(self) -> None:
        title = "Same account transfer"
        http_status = 422
        description = "Origin and destination accounts must be different."
        translation = "A conta de destino precisa ser diferente da conta de origem."
        super().__init__(title, self.code, http_status, description, translation)


class NotFoundDestinationAccount(QIException):
    code = "QIT002014"

    def __init__(self, account_key) -> None:
        title = "Destination account not Found"
        http_status = 404
        description = f"Destination account with key {account_key} was not found."
        translation = f"A conta de destino com chave {account_key} não foi encontrada."
        super().__init__(title, self.code, http_status, description, translation)


class NotFoundTransaction(QIException):
    code = "QIT002015"

    def __init__(self, transaction_key) -> None:
        title = "Transaction not Found"
        http_status = 404
        description = f"Transaction with key {transaction_key} was not found in this account."
        translation = f"A transação com chave {transaction_key} não foi encontrada nesta conta."
        super().__init__(title, self.code, http_status, description, translation)


class RequestControlKeyConflict(QIException):
    code = "QIT002016"

    def __init__(self, request_control_key) -> None:
        title = "Request control key conflict"
        http_status = 409
        description = f"request_control_key {request_control_key} was already used with a different request."
        translation = "Esta request_control_key já foi usada em outra requisição, com dados diferentes."
        super().__init__(title, self.code, http_status, description, translation)


class InvalidBirthdate(QIException):
    code = "QIT002017"

    def __init__(self, birthdate) -> None:
        title = "Invalid birthdate"
        http_status = 422
        description = f"{birthdate} is not a valid date in the past."
        translation = f"{birthdate} não é uma data válida no passado."
        super().__init__(title, self.code, http_status, description, translation)
