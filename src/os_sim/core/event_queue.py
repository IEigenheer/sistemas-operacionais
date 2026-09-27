import heapq
from dataclasses import dataclass, field
from typing import Mapping

from .event import Event, EventType


@dataclass(order=True, slots=True)
class _QueueItem:
    time: int
    sequence: int
    event: Event = field(compare=False)


class EventQueue:
    """Fila de prioridade determinística para eventos discretos."""

    def __init__(self) -> None:
        self._items: list[_QueueItem] = []
        self._next_sequence = 0

    def schedule(
        self,
        time: int,
        event_type: EventType,
        *,
        process_id: str | None = None,
        thread_id: str | None = None,
        payload: Mapping[str, object] | None = None,
    ) -> Event:
        if isinstance(time, bool) or not isinstance(time, int):
            raise TypeError("event time must be an integer")
        if time < 0:
            raise ValueError("event time cannot be negative")
        if not isinstance(event_type, EventType):
            raise TypeError("event type must be an EventType")
        event = Event(
            time=time,
            sequence=self._next_sequence,
            type=event_type,
            process_id=process_id,
            thread_id=thread_id,
            payload={} if payload is None else payload,
        )
        self._next_sequence += 1
        heapq.heappush(self._items, _QueueItem(event.time, event.sequence, event))
        return event

    def pop_next(self) -> Event:
        if not self._items:
            raise IndexError("cannot pop from an empty event queue")
        return heapq.heappop(self._items).event

    def peek(self) -> Event | None:
        return self._items[0].event if self._items else None

    def is_empty(self) -> bool:
        return not self._items

    def __len__(self) -> int:
        return len(self._items)
