from datetime import datetime

from eventide_python.message_db.message_data import ReadMessage, WriteMessage
from eventide_python.message_db.serialization import to_read_message, to_write_message


def test_to_write_message() -> None:
    msg = to_write_message({"type": "Test", "data": {"a": 1}, "metadata": {"b": 2}})
    assert msg == WriteMessage(id=None, type="Test", data={"a": 1}, metadata={"b": 2})


def test_to_read_message() -> None:
    row = {
        "id": "123",
        "stream_name": "stream-1",
        "type": "Test",
        "position": 0,
        "global_position": 1,
        "data": '{"a": 1}',
        "metadata": '{"b": 2}',
        "time": datetime(2024, 1, 1, 0, 0, 0),
    }
    msg = to_read_message(row)
    assert msg == ReadMessage(
        id="123",
        stream_name="stream-1",
        type="Test",
        position=0,
        global_position=1,
        data={"a": 1},
        metadata={"b": 2},
        time=datetime(2024, 1, 1, 0, 0, 0),
    )
