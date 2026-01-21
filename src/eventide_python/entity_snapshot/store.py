from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, Callable, TypeVar

from eventide_python.message_db.client import MessageDBClient
from eventide_python.stream_name import compose as compose_stream_name

EntityType = TypeVar("EntityType")


class SnapshotError(RuntimeError):
    pass


class SnapshotStore:
    def __init__(
        self,
        *,
        message_db: MessageDBClient,
        entity_class: type[EntityType],
        serialize: Callable[[EntityType], dict[str, Any]] | None = None,
        deserialize: Callable[[dict[str, Any]], EntityType] | None = None,
    ) -> None:
        self._message_db = message_db
        self._entity_class = entity_class
        self._serialize = serialize or _default_serialize
        self._deserialize = deserialize or _default_deserialize(entity_class)

    def snapshot_stream_name(self, entity_id: str) -> str:
        category = _entity_category(self._entity_class)
        return compose_stream_name(category, stream_id=entity_id, type="snapshot")

    def put(self, entity_id: str, entity: EntityType, version: int, time: datetime | None) -> int:
        if not isinstance(entity, self._entity_class):
            raise SnapshotError(f"Cannot snapshot {type(entity)} in store for {self._entity_class}")

        data = {
            "entity_data": self._serialize(entity),
            "entity_version": version,
        }
        message = {"type": "Recorded", "data": data}
        stream_name = self.snapshot_stream_name(entity_id)
        return self._message_db.write(message, stream_name)

    def get(self, entity_id: str) -> tuple[EntityType, int, datetime | None] | None:
        stream_name = self.snapshot_stream_name(entity_id)
        message = self._message_db.get_last_stream_message(stream_name)
        if message is None:
            return None
        data = message.data or {}
        entity_data = data.get("entity_data")
        entity_version = data.get("entity_version")
        if entity_data is None or entity_version is None:
            raise SnapshotError("Snapshot message missing entity data or version")
        entity = self._deserialize(entity_data)
        return entity, int(entity_version), message.time


def _default_serialize(entity: Any) -> dict[str, Any]:
    if is_dataclass(entity):
        return asdict(entity)
    if hasattr(entity, "__dict__"):
        return dict(entity.__dict__)
    raise SnapshotError("Entity is not serializable without a custom serializer")


def _default_deserialize(entity_class: type[EntityType]) -> Callable[[dict[str, Any]], EntityType]:
    def _loader(data: dict[str, Any]) -> EntityType:
        try:
            return entity_class(**data)
        except TypeError:
            instance = entity_class()
            for key, value in data.items():
                setattr(instance, key, value)
            return instance

    return _loader


def _entity_category(entity_class: type) -> str:
    name = entity_class.__name__.split(".")[-1]
    if not name:
        return ""
    return name[0].lower() + name[1:]
