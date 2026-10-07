from fastapi import Request
from fastapi import status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers import AccountController, TransactionController
from resources.pagination import page_envelope, read_page
from utils.schema_handler import SchemaHandler


class AccountResource:
    def on_get_by_key(self, account_key: str) -> JSONResponse:
        account = AccountController().get_by_key(account_key)

        return JSONResponse(content=jsonable_encoder(account), status_code=http_status.HTTP_200_OK)

    @SchemaHandler.validate("put_account_status.json")
    def on_put_status(self, account_key: str, payload: dict) -> JSONResponse:
        account = AccountController().change_status(account_key, payload["status"], payload.get("reason"))

        return JSONResponse(content=jsonable_encoder(account), status_code=http_status.HTTP_200_OK)

    @SchemaHandler.validate("post_transaction.json")
    def on_post_transaction(self, account_key: str, payload: dict) -> JSONResponse:
        """201 na primeira execução; 200 quando a mesma request_control_key volta (repetição idempotente)."""
        transaction, created = TransactionController().create(account_key, payload)

        status_code = http_status.HTTP_201_CREATED if created else http_status.HTTP_200_OK

        return JSONResponse(content=jsonable_encoder(transaction), status_code=status_code)

    @SchemaHandler.validate_query_params("get_transactions.json")
    def on_get_transactions(self, account_key: str, request: Request) -> JSONResponse:
        limit, page, offset = read_page(request)
        type_enumerator = request.query_params.get("type")

        statement_page = TransactionController().get_statement(account_key, limit, offset, type_enumerator)

        return JSONResponse(
            content=jsonable_encoder(page_envelope(statement_page, limit, page)),
            status_code=http_status.HTTP_200_OK,
        )

    def on_get_transaction(self, account_key: str, transaction_key: str) -> JSONResponse:
        transaction = TransactionController().get_by_key(account_key, transaction_key)

        return JSONResponse(content=jsonable_encoder(transaction), status_code=http_status.HTTP_200_OK)
