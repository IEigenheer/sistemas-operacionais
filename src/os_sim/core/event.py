from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping


class EventType(str, Enum):
    PROCESS_ARRIVAL = "PROCESS_ARRIVAL"
    THREAD_READY = "THREAD_READY"
    DISPATCH = "DISPATCH"
    CPU_BURST_COMPLETE = "CPU_BURST_COMPLETE"
    THREAD_TERMINATED = "THREAD_TERMINATED"
    PROCESS_TERMINATED = "PROCESS_TERMINATED"


@dataclass(frozen=True, slots=True)
class Event:
    time: int
    sequence: int
    type: EventType
    process_id: str | None = None
    thread_id: str | None = None
    payload: Mapping[str, object] = MappingProxyType({})

    def __post_init__(self) -> None:
        if isinstance(self.time, bool) or not isinstance(self.time, int):
            raise TypeError("event time must be an integer")
        if self.time < 0:
            raise ValueError("event time cannot be negative")
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int):
            raise TypeError("event sequence must be an integer")
        if self.sequence < 0:
            raise ValueError("event sequence cannot be negative")
        if not isinstance(self.type, EventType):
            raise TypeError("event type must be an EventType")
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


@dataclass(frozen=True, slots=True)
class EventRecord:
    time: int
    event_type: EventType
    process_id: str | None
    thread_id: str | None
    description: str
