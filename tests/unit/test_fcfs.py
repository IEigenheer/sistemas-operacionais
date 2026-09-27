import pytest

from os_sim.domain import State, Thread
from os_sim.scheduling import FCFSPolicy


def ready(thread: Thread) -> Thread:
    thread.transition_to(State.READY)
    return thread


def test_fcfs_preserves_enqueue_order_without_changing_state() -> None:
    policy = FCFSPolicy()
    first = ready(Thread("T1", "P1", [1]))
    second = ready(Thread("T2", "P2", [1]))
    policy.enqueue(first)
    policy.enqueue(second)
    assert first.state is State.READY
    assert second.state is State.READY
    assert policy.dequeue_next() is first
    assert policy.dequeue_next() is second
    assert policy.dequeue_next() is None


def test_fcfs_accepts_only_ready_threads() -> None:
    with pytest.raises(ValueError):
        FCFSPolicy().enqueue(Thread("T1", "P1", [1]))
