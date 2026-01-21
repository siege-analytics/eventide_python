import os

import pytest

from eventide_python.message_db import PostgresMessageDBClient


MESSAGE_DB_DSN = os.getenv("MESSAGE_DB_DSN")


pytestmark = pytest.mark.integration


@pytest.mark.skipif(MESSAGE_DB_DSN is None, reason="MESSAGE_DB_DSN is not set")
def test_write_and_read_round_trip() -> None:
    client = PostgresMessageDBClient(MESSAGE_DB_DSN)
    stream_name = "integration_test-123"

    client.write({"type": "Tested", "data": {"value": 1}}, stream_name)
    messages = client.get_stream_messages(stream_name)

    assert messages
    assert messages[-1].type == "Tested"


@pytest.mark.skipif(MESSAGE_DB_DSN is None, reason="MESSAGE_DB_DSN is not set")
def test_category_read_with_consumer_group() -> None:
    client = PostgresMessageDBClient(MESSAGE_DB_DSN)

    client.write({"type": "Tested", "data": {"value": 2}}, "integration_test-1")
    client.write({"type": "Tested", "data": {"value": 3}}, "integration_test-2")

    messages = client.get_category_messages(
        "integration_test",
        consumer_group_member=0,
        consumer_group_size=2,
    )

    assert isinstance(messages, list)
