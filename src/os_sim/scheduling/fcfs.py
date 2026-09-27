from collections import deque

from os_sim.domain.state import State
from os_sim.domain.thread import Thread

from .base import SchedulingPolicy


class FCFSPolicy(SchedulingPolicy):
    """Fila FIFO não preemptiva de threads prontas."""

    def __init__(self) -> None:
        self._ready_queue: deque[Thread] = deque()

    def enqueue(self, thread: Thread) -> None:
        if not isinstance(thread, Thread):
            raise TypeError("FCFS accepts Thread objects")
        if thread.state is not State.READY:
            raise ValueError("FCFS accepts only READY threads")
        self._ready_queue.append(thread)

    def dequeue_next(self) -> Thread | None:
        return self._ready_queue.popleft() if self._ready_queue else None

    def is_empty(self) -> bool:
        return not self._ready_queue

    def __len__(self) -> int:
        return len(self._ready_queue)
