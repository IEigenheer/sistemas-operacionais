from collections.abc import Iterable

from os_sim.domain.process import Process
from os_sim.domain.state import State
from os_sim.domain.thread import Thread
from os_sim.scheduling.base import SchedulingPolicy

from .clock import LogicalClock
from .event import Event, EventRecord, EventType
from .event_queue import EventQueue


class SimulationEngine:
    """Executa a simulação discreta usando uma política de escalonamento."""

    def __init__(
        self, processes: Iterable[Process], scheduler: SchedulingPolicy
    ) -> None:
        process_list = list(processes)
        if not process_list:
            raise ValueError("simulation requires at least one process")
        if any(not isinstance(process, Process) for process in process_list):
            raise TypeError("simulation processes must be Process objects")
        if not isinstance(scheduler, SchedulingPolicy):
            raise TypeError("scheduler must implement SchedulingPolicy")
        process_ids = [process.process_id for process in process_list]
        if len(set(process_ids)) != len(process_ids):
            raise ValueError("process IDs must be unique")
        self.clock = LogicalClock()
        self.events = EventQueue()
        self.scheduler = scheduler
        self._processes = {process.process_id: process for process in process_list}
        self._current_thread: Thread | None = None
        self._records: list[EventRecord] = []
        for process in process_list:
            self.events.schedule(
                process.arrival_time,
                EventType.PROCESS_ARRIVAL,
                process_id=process.process_id,
            )

    @property
    def current_thread(self) -> Thread | None:
        return self._current_thread

    @property
    def processes(self) -> tuple[Process, ...]:
        return tuple(self._processes.values())

    def get_records(self) -> tuple[EventRecord, ...]:
        return tuple(self._records)

    def run(self) -> None:
        while not self.events.is_empty():
            event = self.events.pop_next()
            self.clock.advance_to(event.time)
            self._record_event(event)
            self._handle(event)
            self._dispatch_if_possible()

    def _record_event(self, event: Event) -> None:
        self._records.append(
            EventRecord(
                time=self.clock.now,
                event_type=event.type,
                process_id=event.process_id,
                thread_id=event.thread_id,
                description=event.type.value,
            )
        )

    def _record(
        self,
        event_type: EventType,
        *,
        process_id: str | None = None,
        thread_id: str | None = None,
        description: str | None = None,
    ) -> None:
        self._records.append(
            EventRecord(
                time=self.clock.now,
                event_type=event_type,
                process_id=process_id,
                thread_id=thread_id,
                description=description or event_type.value,
            )
        )

    def _handle(self, event: Event) -> None:
        if event.type is EventType.PROCESS_ARRIVAL:
            self._handle_arrival(event)
        elif event.type is EventType.CPU_BURST_COMPLETE:
            self._handle_burst_complete(event)
        else:
            raise ValueError(f"unsupported simulation event: {event.type.value}")

    def _handle_arrival(self, event: Event) -> None:
        if event.process_id is None:
            raise ValueError("process arrival must identify a process")
        process = self._processes[event.process_id]
        process.transition_to(State.READY)
        for thread in process.threads:
            thread.transition_to(State.READY)
            self.scheduler.enqueue(thread)
            self._record(
                EventType.THREAD_READY,
                process_id=process.process_id,
                thread_id=thread.thread_id,
            )

    def _dispatch_if_possible(self) -> None:
        if self._current_thread is not None:
            return
        thread = self.scheduler.dequeue_next()
        if thread is None:
            return
        process = self._processes[thread.process_id]
        thread.transition_to(State.RUNNING)
        if process.state is State.READY:
            process.transition_to(State.RUNNING)
        elif process.state is not State.RUNNING:
            raise ValueError("a thread can only be dispatched from a ready process")
        self._current_thread = thread
        self._record(
            EventType.DISPATCH,
            process_id=process.process_id,
            thread_id=thread.thread_id,
        )
        self.events.schedule(
            self.clock.now + thread.current_burst(),
            EventType.CPU_BURST_COMPLETE,
            process_id=process.process_id,
            thread_id=thread.thread_id,
        )

    def _handle_burst_complete(self, event: Event) -> None:
        if event.process_id is None or event.thread_id is None:
            raise ValueError("CPU burst completion must identify process and thread")
        thread = self._current_thread
        if thread is None or thread.thread_id != event.thread_id:
            raise ValueError("CPU burst completion does not match the running thread")
        process = self._processes[event.process_id]
        if thread.process_id != process.process_id or thread.state is not State.RUNNING:
            raise ValueError("invalid CPU burst completion target")
        duration = thread.current_burst()
        thread.tcb.program_counter += duration
        thread.complete_current_burst()
        if thread.remaining_bursts:
            thread.transition_to(State.READY)
            process.update_aggregate_state()
            self.scheduler.enqueue(thread)
        else:
            thread.transition_to(State.TERMINATED)
            self._record(
                EventType.THREAD_TERMINATED,
                process_id=process.process_id,
                thread_id=thread.thread_id,
            )
            if process.all_threads_terminated():
                process.transition_to(State.TERMINATED)
                self._record(
                    EventType.PROCESS_TERMINATED,
                    process_id=process.process_id,
                )
            else:
                process.update_aggregate_state()
        self._current_thread = None
