from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import List

from eventide_python.service_host.service import Service

logger = logging.getLogger("eventide_python.service_host")


@dataclass
class Backoff:
    base: float = 0.5
    maximum: float = 5.0
    factor: float = 2.0
    current: float = 0.0

    def reset(self) -> None:
        self.current = 0.0

    def next(self) -> float:
        if self.current == 0.0:
            self.current = self.base
        else:
            self.current = min(self.current * self.factor, self.maximum)
        return self.current


class ServiceHost:
    def __init__(self, *, poll_interval: float = 0.1, backoff: Backoff | None = None) -> None:
        self._services: List[Service] = []
        self._poll_interval = poll_interval
        self._backoff = backoff or Backoff()

    def register(self, service: Service) -> None:
        self._services.append(service)

    def run(self, *, max_iterations: int | None = None) -> None:
        iterations = 0
        while True:
            try:
                for service in self._services:
                    service.run_once()
                self._backoff.reset()
            except Exception as exc:  # noqa: BLE001 - supervisor should catch handler errors
                delay = self._backoff.next()
                logger.exception("Service host error: %s", exc)
                time.sleep(delay)

            iterations += 1
            if max_iterations is not None and iterations >= max_iterations:
                return

            time.sleep(self._poll_interval)
