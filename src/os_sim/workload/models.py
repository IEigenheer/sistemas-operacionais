from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CPUBurst:
    duration: int
