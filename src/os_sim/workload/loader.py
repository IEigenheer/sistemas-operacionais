import json
from pathlib import Path
from typing import Any

from os_sim.domain.process import Process
from os_sim.domain.thread import Thread


class WorkloadValidationError(ValueError):
    """Raised when a workload JSON does not match the MA1 schema."""


class WorkloadLoader:
    def load(self, path: str | Path) -> list[Process]:
        workload_path = Path(path)
        try:
            text = workload_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise WorkloadValidationError(
                f"cannot read workload '{workload_path}': {exc.strerror or exc}"
            ) from exc
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise WorkloadValidationError(
                f"invalid JSON in '{workload_path}': line {exc.lineno} column {exc.colno}"
            ) from exc
        return self._build_processes(data)

    def _build_processes(self, data: Any) -> list[Process]:
        root = self._object(data, "root")
        raw_processes = root.get("processes")
        if not isinstance(raw_processes, list) or not raw_processes:
            raise WorkloadValidationError("'processes' must be a non-empty list")
        processes: list[Process] = []
        process_ids: set[str] = set()
        thread_ids: set[str] = set()
        for index, raw_process in enumerate(raw_processes):
            path = f"processes[{index}]"
            obj = self._object(raw_process, path)
            process_id = self._string(obj, "id", path)
            if process_id in process_ids:
                raise WorkloadValidationError(f"{path}.id: duplicate process ID '{process_id}'")
            process_ids.add(process_id)
            arrival_time = self._integer(obj, "arrival_time", path)
            if arrival_time < 0:
                raise WorkloadValidationError(f"{path}.arrival_time: must be non-negative")
            priority = self._integer(obj, "priority", path)
            raw_threads = obj.get("threads")
            if not isinstance(raw_threads, list) or not raw_threads:
                raise WorkloadValidationError(f"{path}.threads: must be a non-empty list")
            threads: list[Thread] = []
            local_thread_ids: set[str] = set()
            for thread_index, raw_thread in enumerate(raw_threads):
                thread_path = f"{path}.threads[{thread_index}]"
                thread_obj = self._object(raw_thread, thread_path)
                thread_id = self._string(thread_obj, "id", thread_path)
                if thread_id in local_thread_ids:
                    raise WorkloadValidationError(
                        f"{thread_path}.id: duplicate thread ID within process"
                    )
                if thread_id in thread_ids:
                    raise WorkloadValidationError(
                        f"{thread_path}.id: duplicate thread ID in workload"
                    )
                local_thread_ids.add(thread_id)
                thread_ids.add(thread_id)
                raw_bursts = thread_obj.get("bursts")
                if not isinstance(raw_bursts, list) or not raw_bursts:
                    raise WorkloadValidationError(
                        f"{thread_path}.bursts: must be a non-empty list"
                    )
                durations: list[int] = []
                for burst_index, raw_burst in enumerate(raw_bursts):
                    burst_path = f"{thread_path}.bursts[{burst_index}]"
                    burst_obj = self._object(raw_burst, burst_path)
                    burst_type = burst_obj.get("type")
                    if burst_type != "CPU":
                        raise WorkloadValidationError(
                            f"{burst_path}.type: only 'CPU' is supported in MA1"
                        )
                    duration = self._integer(burst_obj, "duration", burst_path)
                    if duration <= 0:
                        raise WorkloadValidationError(
                            f"{burst_path}.duration: must be positive"
                        )
                    durations.append(duration)
                threads.append(Thread(thread_id, process_id, durations))
            processes.append(Process(process_id, arrival_time, priority, threads, arrival_time))
        return processes

    @staticmethod
    def _object(value: Any, path: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise WorkloadValidationError(f"{path}: must be an object")
        return value

    @staticmethod
    def _string(obj: dict[str, Any], key: str, path: str) -> str:
        value = obj.get(key)
        if not isinstance(value, str) or not value.strip():
            raise WorkloadValidationError(f"{path}.{key}: required non-empty string")
        return value

    @staticmethod
    def _integer(obj: dict[str, Any], key: str, path: str) -> int:
        value = obj.get(key)
        if isinstance(value, bool) or not isinstance(value, int):
            raise WorkloadValidationError(f"{path}.{key}: required integer")
        return value
