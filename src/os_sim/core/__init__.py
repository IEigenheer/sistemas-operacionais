"""Núcleo temporal e orientado a eventos da simulação."""

from .clock import LogicalClock
from .event import Event, EventType
from .event_queue import EventQueue

__all__ = ["Event", "EventQueue", "EventType", "LogicalClock"]
