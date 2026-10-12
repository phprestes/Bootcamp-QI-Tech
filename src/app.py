from fastapi import FastAPI

from constants import check_variables
from errors import register_error_handlers
from errors.base_error import error_verification
from middlewares import (
    register_internal_token_middleware,
    register_request_context_middleware,
    register_request_logger_middleware,
    register_session_manager_middleware,
)
from resources import AccountResource, CustomerResource, HealthCheckResource
from utils.logger import setup_logging


def create_app() -> FastAPI:
    """Ordem de leitura: middlewares, rotas, error handlers."""
    application = FastAPI(
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    # O último registrado executa primeiro. Ordem de execução:
    # request_context -> request_logger -> internal_token -> session_manager -> rota.
    # Log antes do token para registrar os 403; sessão por último para não abrir para quem foi barrado.
    # Nenhum teste cobre esta ordem (docs/02-arquitetura/camadas.md).
    register_session_manager_middleware(application)
    register_internal_token_middleware(application)
    register_request_logger_middleware(application)
    register_request_context_middleware(application)

    health_check_resource = HealthCheckResource()

    application.add_api_route("/", health_check_resource.on_get_home, methods=["GET"])
    application.add_api_route(
        "/health_check",
        health_check_resource.on_get_health_check,
        methods=["GET"]
    )

    customer_resource = CustomerResource()
    account_resource = AccountResource()

    application.add_api_route("/customer", customer_resource.on_post, methods=["POST"])
    application.add_api_route("/customer/{customer_key}", customer_resource.on_get_by_key, methods=["GET"])
    application.add_api_route("/customers", customer_resource.on_get_list, methods=["GET"])
    application.add_api_route("/customer/{customer_key}/account", customer_resource.on_post_account, methods=["POST"])
    application.add_api_route("/customer/{customer_key}/accounts", customer_resource.on_get_accounts, methods=["GET"])

    application.add_api_route("/account/{account_key}", account_resource.on_get_by_key, methods=["GET"])
    application.add_api_route("/account/{account_key}/status", account_resource.on_put_status, methods=["PUT"])
    application.add_api_route(
        "/account/{account_key}/transaction",
        account_resource.on_post_transaction,
        methods=["POST"],
    )
    application.add_api_route(
        "/account/{account_key}/transactions",
        account_resource.on_get_transactions,
        methods=["GET"],
    )
    application.add_api_route(
        "/account/{account_key}/transaction/{transaction_key}",
        account_resource.on_get_transaction,
        methods=["GET"],
    )

    register_error_handlers(application)

    return application


def main() -> FastAPI:
    # Falha no boot em vez de na primeira requisição.
    check_variables()
    error_verification()
    setup_logging()

    return create_app()


app = main()
