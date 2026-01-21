from __future__ import annotations

from typing import Protocol


class Service(Protocol):
    def run_once(self) -> None: ...
