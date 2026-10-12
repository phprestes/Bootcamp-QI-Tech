import re
import uuid
from contextvars import ContextVar


REQUEST_ID_HEADER = "X-Request-ID"

# Valor externo vai para o log: restringir evita log injection.
SAFE_REQUEST_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")

NO_REQUEST_ID = "-"


# Em utils/ porque o logger depende dele e não pode importar middlewares/ (ciclo).
_request_id: ContextVar[str] = ContextVar("request_id", default=NO_REQUEST_ID)


def get_request_id() -> str:
    return _request_id.get()


def set_request_id(request_id: str) -> None:
    _request_id.set(request_id)


def build_request_id(received_request_id: str = None) -> str:
    """Reaproveita o id recebido para rastrear entre serviços; fora do formato, gera outro.

    fullmatch, não match: match aceitaria lixo depois de um começo válido.
    """
    if received_request_id is not None and SAFE_REQUEST_ID.fullmatch(received_request_id):
        return received_request_id

    return str(uuid.uuid4())
