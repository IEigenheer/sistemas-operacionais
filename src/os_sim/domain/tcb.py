from dataclasses import dataclass, field

from .state import State


@dataclass(slots=True)
class TCB:
    thread_id: str
    process_id: str
    program_counter: int = 0
    registers: dict[str, int] = field(default_factory=dict)
    logical_stack: list[int] = field(default_factory=list)
    _state: State = field(default=State.NEW, init=False, repr=False)

    @property
    def state(self) -> State:
        return self._state

    def _set_state(self, state: State) -> None:
        self._state = state
