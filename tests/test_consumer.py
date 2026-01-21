from eventide_python.consumer import Consumer, InMemoryPositionStore
from eventide_python.message_db.message_data import ReadMessage


class FakeMessageDBClient:
    def __init__(self, messages: list[ReadMessage]) -> None:
        self._messages = messages

    def iter_category_messages(
        self,
        category,
        position=None,
        batch_size=None,
        correlation=None,
        consumer_group_member=None,
        consumer_group_size=None,
        condition=None,
    ):
        start = 1 if position is None else position
        for message in self._messages:
            if message.global_position >= start:
                yield message


def test_consumer_tracks_position() -> None:
    messages = [
        ReadMessage(
            id="1",
            stream_name="order-1",
            type="Tested",
            position=0,
            global_position=10,
            data={},
            metadata=None,
            time=None,
        ),
        ReadMessage(
            id="2",
            stream_name="order-2",
            type="Tested",
            position=0,
            global_position=11,
            data={},
            metadata=None,
            time=None,
        ),
    ]
    client = FakeMessageDBClient(messages)
    store = InMemoryPositionStore()
    handled = []

    consumer = Consumer(
        name="order-consumer",
        category="order",
        message_db=client,
        handler=lambda msg: handled.append(msg.global_position),
        position_store=store,
    )

    processed = consumer.run_once()

    assert processed == 2
    assert handled == [10, 11]
    assert store.get("order-consumer") == 11
