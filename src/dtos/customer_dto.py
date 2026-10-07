from typing import List

from models import Customer


class CustomerDTO:
    @staticmethod
    def obj_to_dict(customer: Customer) -> dict:
        return {
            "customer_key": customer.customer_key,
            "name": customer.name,
            "document_number": customer.document_number,
            "birthdate": customer.birthdate.isoformat(),
            "created_at": customer.created_at.isoformat(),
        }

    @staticmethod
    def list_obj_to_list_dict(customers: List[Customer]) -> List[dict]:
        return [CustomerDTO.obj_to_dict(customer) for customer in customers]

    @staticmethod
    def only_obj_key(customer: Customer) -> dict:
        return {"customer_key": customer.customer_key}
