from collections.abc import Iterable

from .pcb import PCB
from .state import PROCESS_TRANSITIONS, State, validate_transition
from .thread import Thread


class Process:
    """Process simulado que agrega o estado de suas threads."""

    def __init__(
        self,
        process_id: str,
        arrival_time: int,
        priority: int,
        threads: Iterable[Thread],
        created_at: int = 0,
    ) -> None:
        if not isinstance(process_id, str) or not process_id.strip():
            raise ValueError("process_id must be a non-empty string")
        if isinstance(arrival_time, bool) or not isinstance(arrival_time, int):
            raise TypeError("arrival_time must be an integer")
        if arrival_time < 0:
            raise ValueError("arrival_time cannot be negative")
        if isinstance(priority, bool) or not isinstance(priority, int):
            raise TypeError("priority must be an integer")
        if isinstance(created_at, bool) or not isinstance(created_at, int):
            raise TypeError("created_at must be an integer")
        if created_at < 0:
            raise ValueError("created_at cannot be negative")
        thread_list = list(threads)
        if not thread_list:
            raise ValueError("a process must have at least one thread")
        for thread in thread_list:
            if not isinstance(thread, Thread):
                raise TypeError("process threads must be Thread objects")
            if thread.process_id != process_id:
                raise ValueError("each thread must reference its owning process")
        thread_ids = [thread.thread_id for thread in thread_list]
        if len(set(thread_ids)) != len(thread_ids):
            raise ValueError("thread IDs must be unique within a process")
        self._pcb = PCB(
            process_id=process_id,
            priority=priority,
            arrival_time=arrival_time,
            created_at=created_at,
            thread_ids=thread_ids,
        )
        self._threads = tuple(thread_list)

    @property
    def pcb(self) -> PCB:
        return self._pcb

    @property
    def process_id(self) -> str:
        return self._pcb.process_id

    @property
    def arrival_time(self) -> int:
        return self._pcb.arrival_time

    @property
    def priority(self) -> int:
        return self._pcb.priority

    @property
    def state(self) -> State:
        return self._pcb.state

    @property
    def threads(self) -> tuple[Thread, ...]:
        return self._threads

    def transition_to(self, state: State) -> None:
        if not isinstance(state, State):
            raise TypeError("state must be a State")
        validate_transition(self.state, state, PROCESS_TRANSITIONS)
        self._pcb._set_state(state)

    def all_threads_terminated(self) -> bool:
        return all(thread.state is State.TERMINATED for thread in self._threads)

    def update_aggregate_state(self) -> State:
        if self.all_threads_terminated():
            target = State.TERMINATED
        elif any(thread.state is State.RUNNING for thread in self._threads):
            target = State.RUNNING
        else:
            target = State.READY
        if target is not self.state:
            self.transition_to(target)
        return self.state
