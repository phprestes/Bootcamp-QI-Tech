import os


SERVICE_ROOT = os.path.abspath(os.path.dirname(__file__))

SCHEMA_PATH = os.path.join(SERVICE_ROOT, "schemas")

APP_ENV = os.environ.get("APP_ENV", "local")
SERVICE_NAME = os.environ.get("SERVICE_NAME", "digital-bank-api")

DATABASE_URL = os.environ.get("DATABASE_URL")
INTERNAL_TOKEN = os.environ.get("INTERNAL_TOKEN")

# Birô de CPF: no compose, quem responde é o mock (docs/06-operacao/resiliencia.md).
BUREAU_API_URL = os.environ.get("BUREAU_API_URL", "http://localhost:1080/bureau")
BUREAU_API_INTERNAL_TOKEN = os.environ.get("BUREAU_API_INTERNAL_TOKEN", "default_token")
BUREAU_API_TIMEOUT = int(os.environ.get("BUREAU_API_TIMEOUT", "5"))

# Regras de negócio configuráveis; o valor cobrado fica gravado em cada lançamento FEE.
TRANSFER_FEE_CENTS = int(os.environ.get("TRANSFER_FEE_CENTS", "200"))
MAX_ACCOUNTS_PER_CUSTOMER = int(os.environ.get("MAX_ACCOUNTS_PER_CUSTOMER", "3"))
MINIMUM_CUSTOMER_AGE = 18

# Públicas: raiz e health check (consultado pelo Docker sem token).
BYPASS_ENDPOINTS = [
    "/",
    "/health_check",
]

REQUIRED_VARIABLES = ["DATABASE_URL", "INTERNAL_TOKEN"]


def check_variables():
    missing = []
    for name in REQUIRED_VARIABLES:
        if not globals().get(name):
            missing.append(name)

    if missing:
        raise EnvironmentError(
            f"Faltam variáveis de ambiente: {', '.join(missing)}. "
            "Rodando com 'docker compose up' elas já vêm preenchidas. "
            "Fora do Docker, copie o .env.example para .env."
        )
