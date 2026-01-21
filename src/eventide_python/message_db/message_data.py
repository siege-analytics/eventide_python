from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

JsonObject = Mapping[str, Any]


@dataclass(frozen=True)
class MessageData:
    id: str | None
    type: str
    data: JsonObject | None = None
    metadata: JsonObject | None = None

    def matches_type(self, value: str) -> bool:
        return self.type == value


@dataclass(frozen=True)
class WriteMessage(MessageData):
    pass


@dataclass(frozen=True)
class ReadMessage(MessageData):
    stream_name: str = ""
    position: int = 0
    global_position: int = 0
    time: datetime | None = None
