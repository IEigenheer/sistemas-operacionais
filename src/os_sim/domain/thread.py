from collections.abc import Iterable

from .state import THREAD_TRANSITIONS, InvalidStateTransition, State, validate_transition
from .tcb import TCB


class Thread:
    """Thread simulada, escalonável e sem vínculo com threads do Python."""

    def __init__(self, thread_id: str, process_id: str, cpu_bursts: Iterable[int]) -> None:
        if not isinstance(thread_id, str) or not thread_id.strip():
            raise ValueError("thread_id must be a non-empty string")
        if not isinstance(process_id, str) or not process_id.strip():
            raise ValueError("process_id must be a non-empty string")
        bursts = tuple(cpu_bursts)
        if not bursts:
            raise ValueError("a thread must have at least one CPU burst")
        if any(isinstance(duration, bool) or not isinstance(duration, int) for duration in bursts):
            raise TypeError("CPU burst durations must be integers")
        if any(duration <= 0 for duration in bursts):
            raise ValueError("CPU burst durations must be positive")
        self._tcb = TCB(thread_id=thread_id, process_id=process_id)
        self._cpu_bursts = bursts
        self._burst_index = 0

    @property
    def tcb(self) -> TCB:
        return self._tcb

    @property
    def thread_id(self) -> str:
        return self._tcb.thread_id

    @property
    def process_id(self) -> str:
        return self._tcb.process_id

    @property
    def state(self) -> State:
        return self._tcb.state

    @property
    def cpu_bursts(self) -> tuple[int, ...]:
        return self._cpu_bursts

    @property
    def remaining_bursts(self) -> tuple[int, ...]:
        return self._cpu_bursts[self._burst_index :]

    def current_burst(self) -> int:
        if self._burst_index >= len(self._cpu_bursts):
            raise InvalidStateTransition("thread has no CPU burst remaining")
        return self._cpu_bursts[self._burst_index]

    def complete_current_burst(self) -> None:
        if self._burst_index >= len(self._cpu_bursts):
            raise InvalidStateTransition("thread has no CPU burst remaining")
        self._burst_index += 1

    def transition_to(self, state: State) -> None:
        if not isinstance(state, State):
            raise TypeError("state must be a State")
        validate_transition(self.state, state, THREAD_TRANSITIONS)
        self._tcb._set_state(state)
