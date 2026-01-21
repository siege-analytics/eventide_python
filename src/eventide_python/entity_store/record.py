from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

EntityType = TypeVar("EntityType")


@dataclass(frozen=True)
class EntityRecord(Generic[EntityType]):
    entity_id: str
    entity: EntityType
    version: int | None
    persisted_version: int | None = None
    persisted_time: datetime | None = None
