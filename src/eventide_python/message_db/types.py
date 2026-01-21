from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping


JsonObject = Mapping[str, Any]


@dataclass(frozen=True)
class MessageRecord:
    id: str
    stream_name: str
    type: str
    position: int
    global_position: int
    data: JsonObject | None
    metadata: JsonObject | None
    time: datetime
