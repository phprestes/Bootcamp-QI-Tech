from datetime import date

from tests.utils.random_generator import RandomGenerator


def birthdate_for_age(age_in_years: int) -> str:
    """Data de nascimento de quem faz `age_in_years` hoje; 29/02 recua para 28/02, que existe todo ano."""
    today = date.today()

    if today.month == 2 and today.day == 29:
        return date(today.year - age_in_years, 2, 28).isoformat()

    return date(today.year - age_in_years, today.month, today.day).isoformat()


class PayloadGenerator:
    """Payloads válidos por padrão; qualquer campo pode ser trocado por keyword."""

    @staticmethod
    def create_customer_payload(**overrides) -> dict:
        payload = {
            "name": "Ana Souza",
            "document_number": RandomGenerator.generate_cpf(),
            "birthdate": birthdate_for_age(30),
        }
        payload.update(overrides)
        return payload

    @staticmethod
    def create_deposit_payload(amount: int = 10000, **overrides) -> dict:
        payload = {
            "type": "DEPOSIT",
            "amount": amount,
            "request_control_key": RandomGenerator.generate_uuid(),
        }
        payload.update(overrides)
        return payload

    @staticmethod
    def create_transfer_payload(destination_account_key: str, amount: int = 10000, **overrides) -> dict:
        payload = {
            "type": "TRANSFER",
            "amount": amount,
            "destination_account_key": destination_account_key,
            "request_control_key": RandomGenerator.generate_uuid(),
        }
        payload.update(overrides)
        return payload

    @staticmethod
    def create_status_payload(status: str, reason: str = "requested by test") -> dict:
        return {"status": status, "reason": reason}
