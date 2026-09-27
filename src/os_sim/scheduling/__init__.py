"""Políticas de escalonamento da simulação."""

from .base import SchedulingPolicy
from .fcfs import FCFSPolicy

__all__ = ["FCFSPolicy", "SchedulingPolicy"]
