import time

from fastapi import FastAPI, Request

from constants import BYPASS_ENDPOINTS
from utils.logger import get_logger


logger = get_logger(__name__)


def register_request_logger_middleware(application: FastAPI) -> None:
    """Loga entrada e saída de cada requisição, com status e tempo.

    Nunca loga o corpo (dado sensível) nem as rotas de BYPASS_ENDPOINTS (health check a cada 3 s).
    """

    @application.middleware("http")
    async def log_request(request: Request, call_next):
        if request.url.path in BYPASS_ENDPOINTS:
            return await call_next(request)

        # A query string vai para o log, por isso segredo nunca viaja nela.
        requested_path = request.url.path
        if request.url.query:
            requested_path = f"{requested_path}?{request.url.query}"

        started_at = time.perf_counter()
        logger.info(f"ENTROU {request.method} {requested_path}")

        response = await call_next(request)

        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.info(f"SAIU {response.status_code} {request.method} {request.url.path} - {elapsed_ms:.1f} ms")

        return response
