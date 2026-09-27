import argparse
import sys
from collections.abc import Sequence

from .core.engine import SimulationEngine
from .scheduling.fcfs import FCFSPolicy
from .workload.loader import WorkloadLoader, WorkloadValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Executa o simulador de SO")
    parser.add_argument("--workload", required=True, help="arquivo JSON da carga")
    parser.add_argument("--scheduler", required=True, choices=["fcfs"])
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        processes = WorkloadLoader().load(args.workload)
        engine = SimulationEngine(processes, FCFSPolicy())
        engine.run()
    except (OSError, WorkloadValidationError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"scheduler={args.scheduler} workload={args.workload}")
    for record in engine.get_records():
        subject = []
        if record.process_id is not None:
            subject.append(f"process={record.process_id}")
        if record.thread_id is not None:
            subject.append(f"thread={record.thread_id}")
        suffix = f" {' '.join(subject)}" if subject else ""
        print(f"[t={record.time}] {record.event_type.value}{suffix}")
    print(f"final_clock={engine.clock.now}")
    return 0
