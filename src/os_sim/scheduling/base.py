from abc import ABC, abstractmethod

from os_sim.domain.thread import Thread


class SchedulingPolicy(ABC):
    @abstractmethod
    def enqueue(self, thread: Thread) -> None:
        """Add a READY thread to the policy."""

    @abstractmethod
    def dequeue_next(self) -> Thread | None:
        """Return the next READY thread, or None when empty."""

    @abstractmethod
    def is_empty(self) -> bool:
        """Return whether no thread is waiting."""

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of waiting threads."""
