from fastapi import Request
from fastapi import status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers import AccountController, CustomerController
from resources.pagination import page_envelope, read_page
from utils.schema_handler import SchemaHandler


class CustomerResource:
    @SchemaHandler.validate("post_customer.json")
    def on_post(self, payload: dict) -> JSONResponse:
        customer = CustomerController().create(payload)

        return JSONResponse(content=jsonable_encoder(customer), status_code=http_status.HTTP_201_CREATED)

    def on_get_by_key(self, customer_key: str) -> JSONResponse:
        customer = CustomerController().get_by_key(customer_key)

        return JSONResponse(content=jsonable_encoder(customer), status_code=http_status.HTTP_200_OK)

    @SchemaHandler.validate_query_params("get_customers.json")
    def on_get_list(self, request: Request) -> JSONResponse:
        limit, page, offset = read_page(request)
        document_number = request.query_params.get("document_number")

        customers_page = CustomerController().get_list(limit, offset, document_number)

        return JSONResponse(
            content=jsonable_encoder(page_envelope(customers_page, limit, page)),
            status_code=http_status.HTTP_200_OK,
        )

    def on_post_account(self, customer_key: str) -> JSONResponse:
        account = AccountController().create(customer_key)

        return JSONResponse(content=jsonable_encoder(account), status_code=http_status.HTTP_201_CREATED)

    @SchemaHandler.validate_query_params("get_customer_accounts.json")
    def on_get_accounts(self, customer_key: str, request: Request) -> JSONResponse:
        limit, page, offset = read_page(request)

        accounts_page = AccountController().get_list_by_customer(customer_key, limit, offset)

        return JSONResponse(
            content=jsonable_encoder(page_envelope(accounts_page, limit, page)),
            status_code=http_status.HTTP_200_OK,
        )
