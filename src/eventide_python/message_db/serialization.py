from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Mapping

from eventide_python.message_db.message_data import ReadMessage, WriteMessage


def _parse_json(value: str | None) -> Mapping[str, Any] | None:
    if value is None:
        return None
    return json.loads(value)


def _format_time(value: Any) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def to_write_message(value: dict) -> WriteMessage:
    return WriteMessage(
        id=value.get("id"),
        type=value["type"],
        data=value.get("data"),
        metadata=value.get("metadata"),
    )


def to_read_message(row: Mapping[str, Any]) -> ReadMessage:
    return ReadMessage(
        id=row["id"],
        stream_name=row["stream_name"],
        type=row["type"],
        position=row["position"],
        global_position=row["global_position"],
        data=_parse_json(row.get("data")),
        metadata=_parse_json(row.get("metadata")),
        time=_format_time(row.get("time")),
    )
