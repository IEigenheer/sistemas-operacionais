class LogicalClock:
    """Relógio inteiro da simulação, independente do relógio da máquina."""

    def __init__(self) -> None:
        self._now = 0

    @property
    def now(self) -> int:
        return self._now

    def advance_to(self, target: int) -> None:
        if isinstance(target, bool) or not isinstance(target, int):
            raise TypeError("target must be an integer")
        if target < 0:
            raise ValueError("logical time cannot be negative")
        if target < self._now:
            raise ValueError("logical clock cannot move backwards")
        self._now = target
