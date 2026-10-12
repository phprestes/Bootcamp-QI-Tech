from fastapi import FastAPI, Request

from database import clear_context, open_context


def register_session_manager_middleware(application: FastAPI) -> None:
    """Abre o contexto, faz rollback em exceção e fecha a sessão sempre.

    Nunca dá commit: salvar é decisão do controller (docs/02-arquitetura/camadas.md).
    """

    @application.middleware("http")
    async def manage_session(request: Request, call_next):
        # Sessão preguiçosa: rotas sem controller (/, /health_check) não dependem do banco.
        context = open_context()

        try:
            response = await call_next(request)
        except Exception:
            # O close também desfaria; o rollback deixa a intenção explícita.
            if context.db_session is not None:
                context.db_session.rollback()
            raise
        finally:
            if context.db_session is not None:
                context.db_session.close()

            # Fora de uma requisição, get_context precisa falhar, não devolver sessão fechada.
            clear_context()

        return response
