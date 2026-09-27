import pytest

from os_sim.core.clock import LogicalClock


def test_clock_starts_at_zero_and_advances() -> None:
    clock = LogicalClock()
    assert clock.now == 0
    clock.advance_to(4)
    assert clock.now == 4
    clock.advance_to(4)
    assert clock.now == 4


def test_clock_rejects_negative_and_backward_values() -> None:
    clock = LogicalClock()
    with pytest.raises(ValueError):
        clock.advance_to(-1)
    clock.advance_to(3)
    with pytest.raises(ValueError, match="backwards"):
        clock.advance_to(2)


def test_clock_requires_integer_targets() -> None:
    with pytest.raises(TypeError):
        LogicalClock().advance_to(1.5)
