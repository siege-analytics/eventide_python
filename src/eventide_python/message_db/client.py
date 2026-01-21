from __future__ import annotations

from typing import Iterable, Protocol

from eventide_python.message_db.types import MessageRecord


class MessageDBClient(Protocol):
    """Synchronous Message DB client contract."""

    def write(
        self,
        message_data: dict | Iterable[dict],
        stream_name: str,
        expected_version: int | None = None,
    ) -> int: ...

    def get_stream_messages(
        self,
        stream_name: str,
        position: int | None = None,
        batch_size: int | None = None,
        condition: str | None = None,
    ) -> list[MessageRecord]: ...

    def get_category_messages(
        self,
        category: str,
        position: int | None = None,
        batch_size: int | None = None,
        correlation: str | None = None,
        consumer_group_member: int | None = None,
        consumer_group_size: int | None = None,
        condition: str | None = None,
    ) -> list[MessageRecord]: ...

    def get_last_stream_message(
        self,
        stream_name: str,
        type: str | None = None,
    ) -> MessageRecord | None: ...
