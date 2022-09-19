from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Any

from classes.basic.command import Command


class Handler(ABC):
    @abstractmethod
    def set_next(self, handler: Handler) -> Handler:
        pass

    @abstractmethod
    def handle(self, command: Command) -> Any:
        pass


class AbstractHandler(Handler):
    _next_handler: Handler = None

    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, command: Command) -> Any:
        if self._next_handler:
            return self._next_handler.handle(command)
        return None
