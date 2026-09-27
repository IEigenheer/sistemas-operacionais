import pytest

from os_sim.core.event import EventType
from os_sim.core.event_queue import EventQueue


def test_queue_orders_by_time_then_sequence() -> None:
    queue = EventQueue()
    first = queue.schedule(5, EventType.DISPATCH)
    second = queue.schedule(2, EventType.PROCESS_ARRIVAL)
    third = queue.schedule(5, EventType.THREAD_READY)
    assert [queue.pop_next(), queue.pop_next(), queue.pop_next()] == [second, first, third]


def test_peek_does_not_remove_and_empty_queue_is_documented() -> None:
    queue = EventQueue()
    assert queue.peek() is None
    with pytest.raises(IndexError):
        queue.pop_next()
    event = queue.schedule(0, EventType.PROCESS_ARRIVAL)
    assert queue.peek() == event
    assert len(queue) == 1
    assert not queue.is_empty()


def test_queue_rejects_negative_time() -> None:
    with pytest.raises(ValueError):
        EventQueue().schedule(-1, EventType.DISPATCH)
