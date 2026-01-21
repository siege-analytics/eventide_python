"""Message DB client contract and types."""

from eventide_python.message_db.client import MessageDBClient
from eventide_python.message_db.errors import (
    CategoryError,
    ConsumerGroupError,
    MessageDBError,
    SqlConditionError,
    WrongExpectedVersion,
)
from eventide_python.message_db.message_data import ReadMessage, WriteMessage
from eventide_python.message_db.postgres import PostgresMessageDBClient
from eventide_python.message_db.types import MessageRecord

__all__ = [
    "CategoryError",
    "ConsumerGroupError",
    "MessageDBClient",
    "MessageDBError",
    "MessageRecord",
    "PostgresMessageDBClient",
    "ReadMessage",
    "SqlConditionError",
    "WriteMessage",
    "WrongExpectedVersion",
]
