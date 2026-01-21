from __future__ import annotations

import time
from typing import Callable

from eventide_python.consumer.position_store import PositionStore
from eventide_python.message_db.client import MessageDBClient
from eventide_python.message_db.message_data import ReadMessage


class Consumer:
    def __init__(
        self,
        *,
        name: str,
        category: str,
        message_db: MessageDBClient,
        handler: Callable[[ReadMessage], None],
        position_store: PositionStore,
        batch_size: int | None = None,
        poll_interval: float = 0.5,
        consumer_group_member: int | None = None,
        consumer_group_size: int | None = None,
        correlation: str | None = None,
    ) -> None:
        self._name = name
        self._category = category
        self._message_db = message_db
        self._handler = handler
        self._position_store = position_store
        self._batch_size = batch_size
        self._poll_interval = poll_interval
        self._consumer_group_member = consumer_group_member
        self._consumer_group_size = consumer_group_size
        self._correlation = correlation

    def run_once(self) -> int:
        last_position = self._position_store.get(self._name)
        position = 1 if last_position is None else last_position + 1
        processed = 0

        for message in self._message_db.iter_category_messages(
            self._category,
            position=position,
            batch_size=self._batch_size,
            correlation=self._correlation,
            consumer_group_member=self._consumer_group_member,
            consumer_group_size=self._consumer_group_size,
        ):
            self._handler(message)
            self._position_store.set(self._name, message.global_position)
            processed += 1

        return processed

    def run(self, *, max_iterations: int | None = None) -> None:
        iterations = 0
        while True:
            processed = self.run_once()
            iterations += 1
            if max_iterations is not None and iterations >= max_iterations:
                return
            if processed == 0:
                time.sleep(self._poll_interval)
