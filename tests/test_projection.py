from dataclasses import dataclass

from eventide_python.entity_store.projection import EntityProjection
from eventide_python.message_db.message_data import ReadMessage


@dataclass
class Counter:
    value: int = 0


class CounterProjection(EntityProjection):
    @EntityProjection.apply("Incremented")
    def apply_incremented(self, message: ReadMessage) -> None:
        self.entity.value += message.data["amount"]


def test_projection_applies_handler() -> None:
    entity = Counter()
    projection = CounterProjection(entity)
    projection.apply_message(
        ReadMessage(
            id="1",
            stream_name="counter-1",
            type="Incremented",
            position=0,
            global_position=1,
            data={"amount": 3},
            metadata=None,
            time=None,
        )
    )
    assert entity.value == 3
