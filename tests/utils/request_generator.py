from os import environ

from tests.utils.requisition import ClientRequisition


INTERNAL_TOKEN = environ.get("INTERNAL_TOKEN", "default_token")
HEADERS = {"INTERNAL-TOKEN": INTERNAL_TOKEN}


class RequestGenerator:
    """Um método por rota; cada um devolve (status, json)."""

    @staticmethod
    def _send(method: str, endpoint: str, payload: dict = None, params: dict = None) -> tuple:
        response = ClientRequisition.send(method, endpoint, payload=payload, headers=dict(HEADERS), query_params=params)
        return response.response_status, response.response_json

    @staticmethod
    def POST_customer(customer_payload: dict) -> tuple:
        return RequestGenerator._send("POST", "/customer", payload=customer_payload)

    @staticmethod
    def GET_customer(customer_key: str) -> tuple:
        return RequestGenerator._send("GET", f"/customer/{customer_key}")

    @staticmethod
    def GET_customers(params: dict = None) -> tuple:
        return RequestGenerator._send("GET", "/customers", params=params)

    @staticmethod
    def GET_customer_accounts(customer_key: str, params: dict = None) -> tuple:
        return RequestGenerator._send("GET", f"/customer/{customer_key}/accounts", params=params)

    @staticmethod
    def POST_account(customer_key: str) -> tuple:
        return RequestGenerator._send("POST", f"/customer/{customer_key}/account")

    @staticmethod
    def GET_account(account_key: str) -> tuple:
        return RequestGenerator._send("GET", f"/account/{account_key}")

    @staticmethod
    def PUT_account_status(account_key: str, status_payload: dict) -> tuple:
        return RequestGenerator._send("PUT", f"/account/{account_key}/status", payload=status_payload)

    @staticmethod
    def POST_transaction(account_key: str, transaction_payload: dict) -> tuple:
        return RequestGenerator._send("POST", f"/account/{account_key}/transaction", payload=transaction_payload)

    @staticmethod
    def GET_transactions(account_key: str, params: dict = None) -> tuple:
        return RequestGenerator._send("GET", f"/account/{account_key}/transactions", params=params)

    @staticmethod
    def GET_transaction(account_key: str, transaction_key: str) -> tuple:
        return RequestGenerator._send("GET", f"/account/{account_key}/transaction/{transaction_key}")
