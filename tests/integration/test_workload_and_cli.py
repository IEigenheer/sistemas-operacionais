from pathlib import Path

from os_sim.cli import main
from os_sim.core import EventType, SimulationEngine
from os_sim.scheduling import FCFSPolicy
from os_sim.workload import WorkloadLoader, WorkloadValidationError


ROOT = Path(__file__).parents[2]
WORKLOAD = ROOT / "workloads" / "verification_fcfs.json"


def test_loader_builds_verification_workload() -> None:
    processes = WorkloadLoader().load(WORKLOAD)
    engine = SimulationEngine(processes, FCFSPolicy())
    engine.run()
    assert [
        record.thread_id
        for record in engine.get_records()
        if record.event_type is EventType.DISPATCH
    ] == ["T1", "T2", "T3"]
    assert engine.clock.now == 7


def test_loader_rejects_invalid_burst_type(tmp_path: Path) -> None:
    path = tmp_path / "invalid.json"
    path.write_text(
        '{"processes":[{"id":"P1","arrival_time":0,"priority":1,'
        '"threads":[{"id":"T1","bursts":[{"type":"IO","duration":1}]}]}]}',
        encoding="utf-8",
    )
    try:
        WorkloadLoader().load(path)
    except WorkloadValidationError as exc:
        assert "only 'CPU'" in str(exc)
    else:
        raise AssertionError("invalid burst type was accepted")


def test_cli_prints_log_and_returns_error_for_missing_file(capsys) -> None:
    assert main(["--workload", str(WORKLOAD), "--scheduler", "fcfs"]) == 0
    output = capsys.readouterr().out
    assert "scheduler=fcfs" in output
    assert "DISPATCH process=P1 thread=T1" in output
    assert "DISPATCH process=P2 thread=T2" in output
    assert "DISPATCH process=P3 thread=T3" in output
    assert "final_clock=7" in output
    assert main(["--workload", "missing.json", "--scheduler", "fcfs"]) != 0
    assert "error:" in capsys.readouterr().err
