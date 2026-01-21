from dataclasses import dataclass
from datetime import datetime

from eventide_python.entity_snapshot import SnapshotStore
from eventide_python.message_db.message_data import ReadMessage


@dataclass
class Counter:
    value: int = 0


class FakeMessageDBClient:
    def __init__(self) -> None:
        self.writes = []
        self.last_message: ReadMessage | None = None

    def write(self, message, stream_name, expected_version=None):  # noqa: ANN001 - protocol-like
        self.writes.append((message, stream_name))
        self.last_message = ReadMessage(
            id="1",
            stream_name=stream_name,
            type=message["type"],
            position=0,
            global_position=1,
            data=message["data"],
            metadata=None,
            time=datetime(2024, 1, 1, 0, 0, 0),
        )
        return 0

    def get_last_stream_message(self, stream_name, type=None):  # noqa: ANN001 - protocol-like
        return self.last_message


def test_snapshot_put_and_get() -> None:
    client = FakeMessageDBClient()
    store = SnapshotStore(message_db=client, entity_class=Counter)

    entity = Counter(value=5)
    store.put("123", entity, version=2, time=datetime(2024, 1, 1, 0, 0, 0))

    loaded = store.get("123")
    assert loaded is not None
    loaded_entity, version, time = loaded
    assert loaded_entity.value == 5
    assert version == 2
    assert time == datetime(2024, 1, 1, 0, 0, 0)
