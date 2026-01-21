from __future__ import annotations

from datetime import datetime
from typing import Dict, Generic, TypeVar

from eventide_python.entity_store.record import EntityRecord

EntityType = TypeVar("EntityType")


class EntityCache(Generic[EntityType]):
    def __init__(self) -> None:
        self._records: Dict[str, EntityRecord[EntityType]] = {}

    def get(self, entity_id: str) -> EntityRecord[EntityType] | None:
        return self._records.get(entity_id)

    def put(
        self,
        entity_id: str,
        entity: EntityType,
        version: int | None,
        *,
        persisted_version: int | None = None,
        persisted_time: datetime | None = None,
    ) -> EntityRecord[EntityType]:
        record = EntityRecord(
            entity_id=entity_id,
            entity=entity,
            version=version,
            persisted_version=persisted_version,
            persisted_time=persisted_time,
        )
        self._records[entity_id] = record
        return record

    def delete(self, entity_id: str) -> None:
        self._records.pop(entity_id, None)
