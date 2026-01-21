from __future__ import annotations

from typing import Callable, Generic, Iterable, TypeVar

from eventide_python.entity_store.cache import EntityCache
from eventide_python.entity_store.projection import EntityProjection
from eventide_python.entity_store.record import EntityRecord
from eventide_python.message_db.client import MessageDBClient
from eventide_python.message_db.message_data import ReadMessage
from eventide_python.stream_name import compose as compose_stream_name

EntityType = TypeVar("EntityType")


class EntityStoreError(RuntimeError):
    pass


class EntityStore(Generic[EntityType]):
    def __init__(
        self,
        *,
        message_db: MessageDBClient,
        category: str,
        projection: type[EntityProjection],
        entity_factory: Callable[[], EntityType],
        cache: EntityCache[EntityType] | None = None,
        batch_size: int | None = None,
    ) -> None:
        if not category:
            raise EntityStoreError("Category is not declared")
        if projection is None:
            raise EntityStoreError("Projection is not declared")
        if entity_factory is None:
            raise EntityStoreError("Entity factory is not declared")

        self._message_db = message_db
        self._category = category
        self._projection_class = projection
        self._entity_factory = entity_factory
        self._cache = cache or EntityCache()
        self._batch_size = batch_size
        self.new_entity_probe: Callable[[EntityType], None] | None = None

    def get(
        self,
        entity_id: str,
        *,
        include: str | None = None,
        probe_action: Callable[[ReadMessage], None] | None = None,
    ) -> EntityType | tuple[EntityType | None, int | None] | EntityRecord[EntityType] | None:
        record = self._cache.get(entity_id)

        if record:
            entity = record.entity
            version = record.version
            persisted_version = record.persisted_version
            persisted_time = record.persisted_time
        else:
            entity = self._new_entity()
            version = None
            persisted_version = None
            persisted_time = None

        current_version = self.refresh(entity, entity_id, version, probe_action=probe_action)

        if current_version is not None:
            record = self._cache.put(
                entity_id,
                entity,
                current_version,
                persisted_version=persisted_version,
                persisted_time=persisted_time,
            )

        return _destructure(record, include)

    def fetch(
        self, entity_id: str, *, include: str | None = None
    ) -> EntityType | tuple[EntityType | None, int | None] | EntityRecord[EntityType]:
        res = self.get(entity_id, include=include)
        if res is None:
            entity = self._new_entity()
            if include == "version":
                return entity, None
            return entity
        if isinstance(res, tuple) and res[0] is None:
            entity = self._new_entity()
            return entity, res[1]
        return res

    def refresh(
        self,
        entity: EntityType,
        entity_id: str,
        current_position: int | None,
        *,
        probe_action: Callable[[ReadMessage], None] | None = None,
    ) -> int | None:
        stream_name = self.stream_name(entity_id)
        start_position = self._next_position(current_position)

        projection = self._projection_class(entity)

        for event_data in self._read_stream(stream_name, start_position):
            projection.apply_message(event_data)
            current_position = event_data.position
            if probe_action:
                probe_action(event_data)

        return current_position

    def get_version(self, entity_id: str) -> int | None:
        _, version = self.get(entity_id, include="version")
        return version

    def delete_cache_record(self, entity_id: str) -> None:
        self._cache.delete(entity_id)

    def stream_name(self, entity_id: str) -> str:
        return compose_stream_name(self._category, stream_id=entity_id)

    def _new_entity(self) -> EntityType:
        entity = self._entity_factory()
        if self.new_entity_probe:
            self.new_entity_probe(entity)
        return entity

    def _read_stream(self, stream_name: str, position: int | None) -> Iterable[ReadMessage]:
        return self._message_db.iter_stream_messages(
            stream_name,
            position=position,
            batch_size=self._batch_size,
        )

    @staticmethod
    def _next_position(position: int | None) -> int | None:
        if position is None:
            return None
        return position + 1


def _destructure(
    record: EntityRecord[EntityType] | None, include: str | None
) -> EntityType | tuple[EntityType | None, int | None] | EntityRecord[EntityType] | None:
    if record is None:
        if include == "version":
            return None, None
        return None
    if include == "record":
        return record
    if include == "version":
        return record.entity, record.version
    return record.entity
