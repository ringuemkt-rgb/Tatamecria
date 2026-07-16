"""In-process event bus for the MVP and deterministic tests."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Event:
    name: str
    payload: dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


EventHandler = Callable[[Event], None]


class EventBus:
    """Synchronous local event bus; replaceable by NATS only when scale requires it."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._handlers[event_name].append(handler)

    def publish(self, event: Event) -> None:
        for handler in tuple(self._handlers.get(event.name, [])):
            handler(event)
