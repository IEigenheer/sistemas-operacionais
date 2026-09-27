from enum import Enum


class State(str, Enum):
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    TERMINATED = "TERMINATED"


class InvalidStateTransition(ValueError):
    """Raised when a model object attempts an unsupported state transition."""


THREAD_TRANSITIONS: dict[State, frozenset[State]] = {
    State.NEW: frozenset({State.READY}),
    State.READY: frozenset({State.RUNNING}),
    State.RUNNING: frozenset({State.TERMINATED, State.READY, State.BLOCKED}),
    State.BLOCKED: frozenset({State.READY}),
    State.TERMINATED: frozenset(),
}

PROCESS_TRANSITIONS: dict[State, frozenset[State]] = {
    State.NEW: frozenset({State.READY}),
    State.READY: frozenset({State.RUNNING, State.TERMINATED}),
    State.RUNNING: frozenset({State.READY, State.TERMINATED}),
    State.BLOCKED: frozenset({State.READY}),
    State.TERMINATED: frozenset(),
}


def validate_transition(
    current: State, target: State, allowed: dict[State, frozenset[State]]
) -> None:
    if target not in allowed[current]:
        raise InvalidStateTransition(
            f"invalid state transition: {current.value} -> {target.value}"
        )
