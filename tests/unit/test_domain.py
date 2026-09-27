import pytest

from os_sim.domain import InvalidStateTransition, Process, State, Thread


def make_thread(thread_id: str = "T1", process_id: str = "P1", duration: int = 4) -> Thread:
    return Thread(thread_id, process_id, [duration])


def test_thread_has_simulated_control_block_and_valid_transitions() -> None:
    thread = make_thread()
    assert thread.state is State.NEW
    assert thread.tcb.program_counter == 0
    assert thread.tcb.registers == {}
    assert thread.tcb.logical_stack == []
    with pytest.raises(InvalidStateTransition):
        thread.transition_to(State.RUNNING)
    thread.transition_to(State.READY)
    thread.transition_to(State.RUNNING)
    thread.transition_to(State.TERMINATED)
    with pytest.raises(InvalidStateTransition):
        thread.transition_to(State.READY)


def test_process_requires_owned_unique_threads() -> None:
    with pytest.raises(ValueError):
        Process("P1", 0, 1, [])
    with pytest.raises(ValueError):
        Process("P1", 0, 1, [make_thread("T1"), make_thread("T1")])
    with pytest.raises(ValueError):
        Process("P1", 0, 1, [make_thread("T1", "P2")])


def test_process_terminates_only_after_all_threads() -> None:
    first = make_thread("T1")
    second = make_thread("T2", duration=2)
    process = Process("P1", 0, 1, [first, second])
    process.transition_to(State.READY)
    first.transition_to(State.READY)
    second.transition_to(State.READY)
    process.transition_to(State.RUNNING)
    first.transition_to(State.RUNNING)
    first.transition_to(State.TERMINATED)
    process.update_aggregate_state()
    assert process.state is State.READY
    assert not process.all_threads_terminated()
    process.transition_to(State.RUNNING)
    second.transition_to(State.RUNNING)
    second.transition_to(State.TERMINATED)
    process.update_aggregate_state()
    assert process.state is State.TERMINATED
    assert process.all_threads_terminated()


def test_process_cannot_be_terminated_before_all_threads() -> None:
    thread = make_thread()
    process = Process("P1", 0, 1, [thread])
    process.transition_to(State.READY)
    with pytest.raises(InvalidStateTransition, match="all threads"):
        process.transition_to(State.TERMINATED)


@pytest.mark.parametrize("bursts", [[], [0], [-1], [1.5]])
def test_invalid_cpu_bursts_are_rejected(bursts: list[object]) -> None:
    with pytest.raises((TypeError, ValueError)):
        Thread("T1", "P1", bursts)
