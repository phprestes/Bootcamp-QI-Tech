from uuid import uuid4

from database import Context
from models import Customer


class CustomerRepository:
    def __init__(self, context: Context) -> None:
        self.session = context.db_session

    def create(self, customer_data: dict) -> Customer:
        customer = Customer()
        customer.customer_key = str(uuid4())
        customer.name = customer_data["name"]
        customer.document_number = customer_data["document_number"]
        customer.birthdate = customer_data["birthdate"]

        self.session.add(customer)
        self.session.flush()

        return customer

    def get_by_key(self, customer_key: str) -> Customer:
        return self.session.query(Customer).filter(Customer.customer_key == customer_key).first()

    def get_by_key_for_update(self, customer_key: str) -> Customer:
        return self.session.query(Customer).filter(Customer.customer_key == customer_key).with_for_update().first()

    def get_by_document_number(self, document_number: str) -> Customer:
        return self.session.query(Customer).filter(Customer.document_number == document_number).first()

    def list_page(self, limit: int, offset: int, document_number: str = None) -> list:
        query = self.session.query(Customer)

        if document_number is not None:
            query = query.filter(Customer.document_number == document_number)

        query = query.order_by(Customer.created_at.desc(), Customer.id.desc())

        return query.limit(limit + 1).offset(offset).all()
