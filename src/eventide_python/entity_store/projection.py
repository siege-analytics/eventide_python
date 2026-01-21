from __future__ import annotations

from typing import Any, Callable, Dict, TypeVar

from eventide_python.message_db.message_data import ReadMessage

Handler = Callable[["EntityProjection", ReadMessage], None]
T = TypeVar("T", bound="EntityProjection")


class ProjectionError(RuntimeError):
    pass


class EntityProjection:
    _handlers: Dict[str, Handler] = {}

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls._handlers = dict(getattr(cls, "_handlers", {}))

    def __init__(self, entity: Any) -> None:
        self.entity = entity

    @classmethod
    def apply(cls: type[T], event_type: str | type) -> Callable[[Handler], Handler]:
        name = event_type.__name__ if isinstance(event_type, type) else str(event_type)

        def decorator(handler: Handler) -> Handler:
            if handler.__code__.co_argcount != 2:
                raise ProjectionError(
                    f"Handler for {name} must accept exactly one message argument."
                )
            cls._handlers[name] = handler
            return handler

        return decorator

    @classmethod
    def when(cls: type[T], event_type: str | type) -> Callable[[Handler], Handler]:
        return cls.apply(event_type)

    @classmethod
    def handles(cls, message: ReadMessage) -> bool:
        return message.type in cls._handlers

    def apply_message(self, message: ReadMessage) -> None:
        handler = self._handlers.get(message.type)
        if handler is not None:
            handler(self, message)
            return
        if hasattr(self, "apply"):
            self.apply(message)
