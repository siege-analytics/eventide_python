from __future__ import annotations

from typing import Dict, Protocol


class PositionStore(Protocol):
    def get(self, consumer_name: str) -> int | None: ...

    def set(self, consumer_name: str, position: int) -> None: ...


class InMemoryPositionStore:
    def __init__(self) -> None:
        self._positions: Dict[str, int] = {}

    def get(self, consumer_name: str) -> int | None:
        return self._positions.get(consumer_name)

    def set(self, consumer_name: str, position: int) -> None:
        self._positions[consumer_name] = position
