from dataclasses import dataclass

from eventide_python.entity_store import EntityStore
from eventide_python.entity_store.projection import EntityProjection
from eventide_python.message_db.message_data import ReadMessage


@dataclass
class Counter:
    value: int = 0


class CounterProjection(EntityProjection):
    @EntityProjection.apply("Incremented")
    def apply_incremented(self, message: ReadMessage) -> None:
        self.entity.value += message.data["amount"]


class FakeMessageDBClient:
    def __init__(self, streams: dict[str, list[ReadMessage]]) -> None:
        self._streams = streams

    def iter_stream_messages(self, stream_name, position=None, batch_size=None, condition=None):
        start = 0 if position is None else position
        for message in self._streams.get(stream_name, []):
            if message.position >= start:
                yield message


def test_entity_store_hydrates_from_stream() -> None:
    stream_name = "counter-123"
    messages = [
        ReadMessage(
            id="1",
            stream_name=stream_name,
            type="Incremented",
            position=0,
            global_position=1,
            data={"amount": 2},
            metadata=None,
            time=None,
        ),
        ReadMessage(
            id="2",
            stream_name=stream_name,
            type="Incremented",
            position=1,
            global_position=2,
            data={"amount": 5},
            metadata=None,
            time=None,
        ),
    ]
    client = FakeMessageDBClient({stream_name: messages})
    store = EntityStore(
        message_db=client,
        category="counter",
        projection=CounterProjection,
        entity_factory=Counter,
    )

    entity, version = store.get("123", include="version")
    assert entity is not None
    assert entity.value == 7
    assert version == 1


def test_fetch_returns_new_entity_when_empty() -> None:
    client = FakeMessageDBClient({})
    store = EntityStore(
        message_db=client,
        category="counter",
        projection=CounterProjection,
        entity_factory=Counter,
    )

    entity = store.fetch("missing")
    assert entity.value == 0
