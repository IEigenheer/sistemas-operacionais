from os_sim.core import EventType, SimulationEngine
from os_sim.domain import Process, State, Thread
from os_sim.scheduling import FCFSPolicy


def build_scenario() -> SimulationEngine:
    processes = [
        Process("P1", 0, 2, [Thread("T1", "P1", [4])]),
        Process("P2", 1, 2, [Thread("T2", "P2", [2])]),
        Process("P3", 1, 2, [Thread("T3", "P3", [1])]),
    ]
    return SimulationEngine(processes, FCFSPolicy())


def test_fcfs_scenario_is_deterministic_and_completes() -> None:
    first = build_scenario()
    second = build_scenario()
    first.run()
    second.run()
    first_records = first.get_records()
    second_records = second.get_records()
    assert first_records == second_records
    dispatches = [record.thread_id for record in first_records if record.event_type is EventType.DISPATCH]
    assert dispatches == ["T1", "T2", "T3"]
    terminations = {
        record.thread_id: record.time
        for record in first_records
        if record.event_type is EventType.THREAD_TERMINATED
    }
    assert terminations == {"T1": 4, "T2": 6, "T3": 7}
    assert first.clock.now == 7
    assert all(process.state is State.TERMINATED for process in first.processes)
    assert all(thread.state is State.TERMINATED for process in first.processes for thread in process.threads)
