from dataclasses import dataclass, field

from .state import State


@dataclass(slots=True)
class PCB:
    process_id: str
    priority: int
    arrival_time: int
    created_at: int
    thread_ids: list[str] = field(default_factory=list)
    _state: State = field(default=State.NEW, init=False, repr=False)

    @property
    def state(self) -> State:
        return self._state

    def _set_state(self, state: State) -> None:
        self._state = state
