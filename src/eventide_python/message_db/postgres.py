from __future__ import annotations

import json
import uuid
from typing import Iterable, Iterator

import psycopg
from psycopg.rows import dict_row

from eventide_python.message_db.errors import (
    CategoryError,
    ConsumerGroupError,
    MessageDBError,
    SqlConditionError,
    WrongExpectedVersion,
)
from eventide_python.message_db.logging import get_logger
from eventide_python.message_db.message_data import ReadMessage, WriteMessage
from eventide_python.message_db.serialization import to_read_message, to_write_message
from eventide_python.message_db.sql import (
    GET_CATEGORY_MESSAGES,
    GET_LAST_STREAM_MESSAGE,
    GET_STREAM_MESSAGES,
    WRITE_MESSAGE,
)

NO_STREAM = -1


class PostgresMessageDBClient:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._logger = get_logger()

    def write(
        self,
        message_data: dict | Iterable[dict],
        stream_name: str,
        expected_version: int | None = None,
    ) -> int:
        batch = self._to_write_batch(message_data)
        expected_version = _canonize_expected_version(expected_version)

        self._logger.debug(
            "Writing %s messages to %s with expected_version=%s",
            len(batch),
            stream_name,
            expected_version,
        )

        with self._connect() as conn:
            with conn.transaction():
                position: int | None = None
                for message in batch:
                    position = self._write_one(conn, message, stream_name, expected_version)
        if position is None:
            raise MessageDBError("Write failed to return a position")
        return position

    def get_stream_messages(
        self,
        stream_name: str,
        position: int | None = None,
        batch_size: int | None = None,
        condition: str | None = None,
    ) -> list[ReadMessage]:
        with self._connect() as conn:
            rows = self._fetch_all(
                conn,
                f"SELECT * FROM {GET_STREAM_MESSAGES}(%s, %s, %s, %s)",
                (stream_name, position, batch_size, condition),
            )
        return [to_read_message(row) for row in rows]

    def get_category_messages(
        self,
        category: str,
        position: int | None = None,
        batch_size: int | None = None,
        correlation: str | None = None,
        consumer_group_member: int | None = None,
        consumer_group_size: int | None = None,
        condition: str | None = None,
    ) -> list[ReadMessage]:
        with self._connect() as conn:
            rows = self._fetch_all(
                conn,
                f"SELECT * FROM {GET_CATEGORY_MESSAGES}(%s, %s, %s, %s, %s, %s, %s)",
                (
                    category,
                    position,
                    batch_size,
                    correlation,
                    consumer_group_member,
                    consumer_group_size,
                    condition,
                ),
            )
        return [to_read_message(row) for row in rows]

    def get_last_stream_message(self, stream_name: str, type: str | None = None) -> ReadMessage | None:
        with self._connect() as conn:
            rows = self._fetch_all(
                conn,
                f"SELECT * FROM {GET_LAST_STREAM_MESSAGE}(%s, %s)",
                (stream_name, type),
            )
        if not rows:
            return None
        return to_read_message(rows[0])

    def iter_stream_messages(
        self,
        stream_name: str,
        position: int | None = None,
        batch_size: int | None = None,
        condition: str | None = None,
    ) -> Iterator[ReadMessage]:
        position = 0 if position is None else position
        batch_size = 1000 if batch_size is None else batch_size

        while True:
            batch = self.get_stream_messages(
                stream_name,
                position=position,
                batch_size=batch_size,
                condition=condition,
            )
            if not batch:
                return
            for message in batch:
                yield message
            position = batch[-1].position + 1
            if len(batch) < batch_size:
                return

    def iter_category_messages(
        self,
        category: str,
        position: int | None = None,
        batch_size: int | None = None,
        correlation: str | None = None,
        consumer_group_member: int | None = None,
        consumer_group_size: int | None = None,
        condition: str | None = None,
    ) -> Iterator[ReadMessage]:
        position = 1 if position is None else position
        batch_size = 1000 if batch_size is None else batch_size

        while True:
            batch = self.get_category_messages(
                category,
                position=position,
                batch_size=batch_size,
                correlation=correlation,
                consumer_group_member=consumer_group_member,
                consumer_group_size=consumer_group_size,
                condition=condition,
            )
            if not batch:
                return
            for message in batch:
                yield message
            position = batch[-1].global_position + 1
            if len(batch) < batch_size:
                return

    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(self._dsn, row_factory=dict_row)

    def _fetch_all(self, conn: psycopg.Connection, query: str, params: tuple) -> list[dict]:
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return list(cur.fetchall())
        except psycopg.Error as exc:  # pragma: no cover - exercised in integration tests
            raise _map_error(exc) from exc

    def _write_one(
        self,
        conn: psycopg.Connection,
        message: WriteMessage,
        stream_name: str,
        expected_version: int | None,
    ) -> int:
        data = json.dumps(message.data) if message.data is not None else None
        metadata = json.dumps(message.metadata) if message.metadata is not None else None
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT {WRITE_MESSAGE}(%s, %s, %s, %s, %s, %s)",
                    (message.id, stream_name, message.type, data, metadata, expected_version),
                )
                return int(cur.fetchone()[0])
        except psycopg.Error as exc:  # pragma: no cover - exercised in integration tests
            context = f"stream_name={stream_name} expected_version={expected_version}"
            raise _map_error(exc, context=context) from exc

    def _to_write_batch(self, message_data: dict | Iterable[dict]) -> list[WriteMessage]:
        if isinstance(message_data, Iterable) and not isinstance(message_data, (dict, str, bytes)):
            batch = message_data
        else:
            batch = [message_data]
        messages: list[WriteMessage] = []
        for item in batch:
            message = to_write_message(item)
            if message.id is None:
                message = WriteMessage(
                    id=str(uuid.uuid4()),
                    type=message.type,
                    data=message.data,
                    metadata=message.metadata,
                )
            messages.append(message)
        return messages


def _canonize_expected_version(value: int | str | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, str) and value.lower() == "no_stream":
        return NO_STREAM
    return int(value)


def _map_error(exc: psycopg.Error, *, context: str | None = None) -> MessageDBError:
    message = str(exc)
    normalized = message.lower()
    if context:
        message = f"{message} ({context})"
    if "wrong expected version" in normalized:
        return WrongExpectedVersion(message)
    if "must be a stream name" in normalized or "must be a category" in normalized:
        return CategoryError(message)
    if "consumer group" in normalized:
        return ConsumerGroupError(message)
    if "sql condition is not activated" in normalized:
        return SqlConditionError(message)
    return MessageDBError(message)
