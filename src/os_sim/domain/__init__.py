"""Entidades do domínio da simulação."""

from .pcb import PCB
from .process import Process
from .state import InvalidStateTransition, State
from .tcb import TCB
from .thread import Thread

__all__ = ["InvalidStateTransition", "PCB", "Process", "State", "TCB", "Thread"]
