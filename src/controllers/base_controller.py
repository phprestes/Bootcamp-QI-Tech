from abc import ABCMeta

from database import get_context
from utils.logger import get_logger


class BaseController(metaclass=ABCMeta):
    """Pega contexto, sessão e logger. Construir um controller é declarar que usa banco."""

    def __init__(self, class_name: str) -> None:
        self.context = get_context()
        self.session = self.context.get_or_create_session()
        self.logger = get_logger(class_name)
