"""Engine, sessão e o contexto por requisição que carrega a sessão.

Por que contexto e não Depends(get_db): docs/02-arquitetura/camadas.md.
"""

from contextvars import ContextVar
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from constants import DATABASE_URL


engine = create_engine(DATABASE_URL, pool_size=5, pool_recycle=600, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Context:
    """Estado de uma requisição. Hoje só a sessão, criada sob demanda.

    Objeto mutável porque o ContextVar é copiado para a task da rota: um .set() na
    rota não chega ao middleware, mas a mutação deste objeto chega.
    """

    def __init__(self) -> None:
        self.db_session: Optional[Session] = None

    def get_or_create_session(self) -> Session:
        if self.db_session is None:
            self.db_session = SessionLocal()

        return self.db_session


_context: ContextVar[Optional[Context]] = ContextVar("context", default=None)


def open_context() -> Context:
    """Chamada só pelo session_manager, que também fecha a sessão."""
    context = Context()
    _context.set(context)

    return context


def clear_context() -> None:
    """Evita que código fora de requisição reuse uma sessão já fechada."""
    _context.set(None)


def get_context() -> Context:
    """Só o controller chama. Devolve o contexto, não a sessão, para o repository
    poder receber mais coisas sem mudar assinatura."""
    context = _context.get()

    if context is None:
        raise Exception(
            "Nao existe contexto neste trabalho. "
            + "Quem prepara o contexto de cada requisicao e o middleware "
            + "src/middlewares/session_manager.py. Se voce chegou aqui, ele nao rodou."
        )

    return context
